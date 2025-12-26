import subprocess
import json
from pathlib import Path
from enum import Enum, auto
from typing import Union, Optional


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
    ):
        self.path = Path(path)
        self.video_type = video_type
        self._aspect_ratio = aspect_ratio
        self._name: Optional[str] = None

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
