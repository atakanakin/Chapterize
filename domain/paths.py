from pathlib import Path
from typing import Union

from core.config import (
    BASE_DATA_DIR,
    AUDIO_DIR,
    TRANSCRIPT_DIR,
    CHAPTER_DIR,
    VIDEO_DIR,
    FRAME_DIR,
    SUBTITLE_DIR,
    SHORT_DIR,
    FINAL_DIR,
)


class Paths:
    """
    Singleton-style path manager.
    Centralizes directory structure and ensures existence upon access.
    """

    _root: Path = BASE_DATA_DIR
    AUDIO_DIR = AUDIO_DIR
    TRANSCRIPTS_DIR = TRANSCRIPT_DIR
    CHAPTERS_DIR = CHAPTER_DIR
    VIDEO_DIR = VIDEO_DIR
    FRAME_DIR = FRAME_DIR
    SUBTITLES_DIR = SUBTITLE_DIR
    SHORTS_DIR = SHORT_DIR
    FINAL_DIR = FINAL_DIR

    @classmethod
    def configure(cls, new_base_dir: Union[str, Path]) -> None:
        """
        Updates the root directory for the entire application.
        All subsequent calls will use this new base.
        """
        cls._root = Path(new_base_dir)

    @classmethod
    def _ensure(cls, path: Path) -> Path:
        """Internal helper to create directory if not exists."""
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def get_audio_dir(cls) -> Path:
        return cls._ensure(cls._root / cls.AUDIO_DIR)

    @classmethod
    def get_transcript_dir(cls) -> Path:
        return cls._ensure(cls._root / cls.TRANSCRIPTS_DIR)

    @classmethod
    def get_chapter_dir(cls) -> Path:
        return cls._ensure(cls._root / cls.CHAPTERS_DIR)

    @classmethod
    def get_video_dir(cls) -> Path:
        return cls._ensure(cls._root / cls.VIDEO_DIR)

    @classmethod
    def get_frame_dir(cls) -> Path:
        return cls._ensure(cls._root / cls.FRAME_DIR)

    @classmethod
    def get_subtitle_dir(cls) -> Path:
        return cls._ensure(cls._root / cls.SUBTITLES_DIR)

    @classmethod
    def get_short_output_dir(cls) -> Path:
        return cls._ensure(cls._root / cls.SHORTS_DIR)

    @classmethod
    def get_final_dir(cls) -> Path:
        return cls._ensure(Path.cwd().parent / cls.FINAL_DIR)

    @classmethod
    def get_lock_file(cls) -> Path:
        return cls._root / ".lock"
