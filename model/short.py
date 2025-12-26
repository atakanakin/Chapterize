from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from model.chapter import Chapter


@dataclass
class Short:
    """
    Represents a processed short clip combining source chapter info
    and generated assets (subtitles, text files, etc.).
    """

    chapter: Chapter
    subtitle_path: Path
    title_text_path: Optional[Path] = None
    final_video_path: Optional[Path] = None
