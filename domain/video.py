import subprocess
import json
from pathlib import Path
from enum import Enum, auto
from typing import Union, Optional
from domain.paths import Paths
from model.streamer import StreamerBBox
from service.detect_streamer import detect_streamer
from service.render_video import render_video
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

    def crop_and_burn_subtitle(
        self,
        subtitle_path: Union[str, Path],
        output_path: Union[str, Path],
        fonts_dir: Union[str, Path] = Paths.get_font_dir(),
    ) -> "Video":
        """Crops video to streamer bounding box and burns in subtitles. Returns new Video instance."""
        subtitle_path = Path(subtitle_path)
        output_path = Path(output_path)

        render_video(
            video_path=self.path,
            subtitle_path=subtitle_path,
            output_path=output_path,
            bbox=self.streamer_bbox,
            fonts_dir=fonts_dir,
        )

        return Video(
            path=output_path,
            video_type=VideoType.FINAL,
            aspect_ratio=self._aspect_ratio,
        )
