from dataclasses import dataclass
from typing import List


@dataclass
class Chapter:
    title: str
    start: float
    end: float
    engagement_score: float


@dataclass
class ChapterizeResult:
    chapters: List[Chapter]
