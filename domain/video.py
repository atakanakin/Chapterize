import subprocess
import json
from pathlib import Path
from enum import Enum, auto
from typing import Union, Optional
from model.streamer import StreamerBBox
from service.detect_streamer import detect_streamer
from utils.extract_frames import extract_frames


class VideoType(Enum):
    ORIGINAL = auto()
    WITHOUT_AUDIO = auto()
    CROPPED = auto()
    SUBCLIP = auto()
    FINAL = auto()


class Video:
    def __init__(
        self,
        path: Union[str, Path],
        video_type: VideoType = VideoType.ORIGINAL,
        aspect_ratio: Optional[tuple[int, int]] = None,  # (width, height)
        streamer_bbox: Optional[StreamerBBox] = None,
    ):
        self.path = Path(path)
        self.video_type = video_type
        self._aspect_ratio = aspect_ratio
        self._name: Optional[str] = None
        self.streamer_bbox = streamer_bbox

    @property
    def name(self) -> str:
        """
        Returns filename without extension using lazy loading.
        """
        if self._name is not None:
            return self._name

        self._name = self.path.stem
        return self._name

    @property
    def resolution(self) -> tuple[int, int]:
        """
        Returns (width, height). Uses cached value if available, otherwise probes file.
        """
        if self._aspect_ratio:
            return self._aspect_ratio

        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "json",
            str(self.path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        stream = info["streams"][0]

        self._aspect_ratio = (stream["width"], stream["height"])
        return self._aspect_ratio

    def add_audio(
        self, audio_path: Union[str, Path], output_path: Union[str, Path]
    ) -> "Video":
        """Merges video with external audio using AAC encoding."""
        audio_path = Path(audio_path)
        output_path = Path(output_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if self.streamer_bbox is None:
            self.streamer_bbox = self.get_streamer_bbox()

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(self.path),
            "-i",
            str(audio_path),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            str(output_path),
        ]

        subprocess.run(cmd, check=True)

        return Video(
            path=output_path,
            video_type=VideoType.ORIGINAL,
            aspect_ratio=self._aspect_ratio,
            streamer_bbox=self.streamer_bbox,
        )

    def extract_subclip(
        self, start_time: float, end_time: float, output_path: Union[str, Path]
    ) -> "Video":
        """Cuts a subclip without re-encoding"""
        output_path = Path(output_path)

        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            str(start_time),
            "-to",
            str(end_time),
            "-i",
            str(self.path),
            "-c",
            "copy",
            str(output_path),
        ]

        subprocess.run(cmd, check=True)

        return Video(
            path=output_path,
            video_type=VideoType.SUBCLIP,
            aspect_ratio=self._aspect_ratio,
            streamer_bbox=self.streamer_bbox,
        )

    def get_streamer_bbox(self) -> Optional[StreamerBBox]:
        """Detects streamer bounding box using Gemini model."""

        frames = extract_frames(video_path=self.path, frame_count=2)
        streamer_detection = detect_streamer(frames)
        print(f"Streamer Detection: {streamer_detection}")
        return streamer_detection.bounding_box

    def smart_vertical_crop(
        self,
        output_path: Union[str, Path],
        target_width: int = 1080,
        target_height: int = 1920,
        streamer_aspect_ratio: float = 6 / 16,
    ) -> "Video":
        """
        Smartly crops the video to vertical format with split-screen support.

        Logic:
        - Calculates split heights based on 6/16 (Top) and 10/16 (Bottom) ratios.
        - Streamer Crop: Uses 'Crop to Fill' strategy inside the BBox to avoid stretching.
        - Content Crop: Standard center crop to fill the bottom area.
        """
        output_path = Path(output_path)
        source_w, source_h = self.resolution

        top_height = int(target_height * (streamer_aspect_ratio))
        bottom_height = target_height - top_height

        # --- CASE 1: No Streamer (Standard Center Crop) ---
        if self.streamer_bbox is None:
            print("No streamer detected, performing standard center crop.")
            return self.resize_with_crop(
                output_path=output_path,
                target_width=target_width,
                target_height=target_height,
            )

        print("Streamer detected, performing smart vertical crop.")

        # --- PART A: Top (Streamer) - "Crop to Fill" Logic ---
        # We treat the BBox as the source video and target_width x top_height as the destination.

        # 1. Get BBox dimensions in pixels
        bbox_x = self.streamer_bbox.x * source_w
        bbox_y = self.streamer_bbox.y * source_h
        bbox_w = self.streamer_bbox.width * source_w
        bbox_h = self.streamer_bbox.height * source_h

        # 2. Calculate Aspect Ratios
        target_top_ratio = target_width / top_height
        current_bbox_ratio = bbox_w / bbox_h

        # 3. Determine Crop Dimensions (inside the BBox)
        if current_bbox_ratio > target_top_ratio:
            # BBox is wider than target slot -> Crop sides (preserve height)
            crop_h = bbox_h
            crop_w = bbox_h * target_top_ratio
        else:
            # BBox is taller than target slot -> Crop top/bottom (preserve width)
            crop_w = bbox_w
            crop_h = bbox_w / target_top_ratio

        # 4. Center the crop within the BBox
        # Center X of BBox = bbox_x + (bbox_w / 2)
        # Top-Left X of Crop = Center X - (crop_w / 2)
        crop_x = (bbox_x + (bbox_w / 2)) - (crop_w / 2)
        crop_y = (bbox_y + (bbox_h / 2)) - (crop_h / 2)

        # 5. Create Filter String (Crop -> Scale)
        # We cast to int() for FFmpeg
        top_filter = (
            f"crop={int(crop_w)}:{int(crop_h)}:{int(crop_x)}:{int(crop_y)},"
            f"scale={target_width}:{top_height}"
        )

        # --- PART B: Bottom (Content) - "Crop to Fill" Logic ---
        # Target is target_width x bottom_height

        target_bottom_ratio = target_width / bottom_height
        current_video_ratio = source_w / source_h

        if current_video_ratio > target_bottom_ratio:
            # Video is wider -> Crop sides
            g_crop_h = source_h
            g_crop_w = source_h * target_bottom_ratio
            g_crop_x = (source_w - g_crop_w) / 2
            g_crop_y = 0
        else:
            # Video is taller -> Crop top/bottom
            g_crop_w = source_w
            g_crop_h = source_w / target_bottom_ratio
            g_crop_x = 0
            g_crop_y = (source_h - g_crop_h) / 2

        content_filter = (
            f"crop={int(g_crop_w)}:{int(g_crop_h)}:{int(g_crop_x)}:{int(g_crop_y)},"
            f"scale={target_width}:{bottom_height}"
        )

        # --- PART C: Combine ---
        filter_complex = (
            f"[0:v]{top_filter}[top];"
            f"[0:v]{content_filter}[bottom];"
            f"[top][bottom]vstack=inputs=2"
        )

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(self.path),
            "-filter_complex",
            filter_complex,
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "copy",
            str(output_path),
        ]

        subprocess.run(cmd, check=True)

        return Video(
            path=output_path,
            video_type=VideoType.CROPPED,
            aspect_ratio=(target_width, target_height),
        )

    def resize_with_crop(
        self,
        output_path: Union[str, Path],
        target_width: int = 1080,
        target_height: int = 1920,
    ) -> "Video":
        """Resizes video to target resolution, cropping center if necessary."""
        output_path = Path(output_path)

        current_width, current_height = self.resolution
        target_ratio = target_width / target_height
        current_ratio = current_width / current_height

        base_cmd = ["ffmpeg", "-y", "-i", str(self.path)]
        filter_cmd = []

        if current_ratio <= target_ratio:
            filter_cmd = [
                "-vf",
                f"scale={target_width}:{target_height}",
                "-c:a",
                "copy",
            ]
        else:
            src_crop_width = int(current_height * target_ratio)
            src_crop_height = current_height
            x_offset = int((current_width - src_crop_width) / 2)

            vf_string = f"crop={src_crop_width}:{src_crop_height}:{x_offset}:0,scale={target_width}:{target_height}"

            filter_cmd = [
                "-vf",
                vf_string,
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "18",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "copy",
            ]

        full_cmd = base_cmd + filter_cmd + [str(output_path)]
        subprocess.run(full_cmd, check=True)

        return Video(
            path=output_path,
            video_type=VideoType.CROPPED,
            aspect_ratio=(target_width, target_height),
        )

    def burn_in_subtitle(
        self,
        subtitle_path: Union[str, Path],
        output_path: Union[str, Path],
        crf: int = 18,
        preset: str = "slow",
        fonts_dir: str = "assets/fonts",
    ) -> "Video":
        """Burns .ass subtitles into video (Re-encodes video)."""
        subtitle_path = Path(subtitle_path)
        output_path = Path(output_path)

        if not subtitle_path.exists():
            raise FileNotFoundError(f"Subtitle file not found: {subtitle_path}")

        vf_string = f"ass='{str(subtitle_path)}':fontsdir='{fonts_dir}'"

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(self.path),
            "-vf",
            vf_string,
            "-c:v",
            "libx264",
            "-crf",
            str(crf),
            "-preset",
            preset,
            "-pix_fmt",
            "yuv420p",
            "-profile:v",
            "high",
            "-level",
            "4.2",
            "-movflags",
            "+faststart",
            "-c:a",
            "copy",
            str(output_path),
        ]

        subprocess.run(cmd, check=True)

        return Video(
            path=output_path,
            video_type=VideoType.FINAL,
            aspect_ratio=self._aspect_ratio,
        )
