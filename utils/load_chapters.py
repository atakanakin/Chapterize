from pathlib import Path
import json
from core.config import ENGAGEMENT_THRESHOLD
from model.chapter import Chapter
from typing import List


def load_chapters(
    chapter_path: Path, filter_low_engagement: bool = False
) -> List[Chapter]:
    with open(chapter_path, "r", encoding="utf-8") as f:
        data = json.load(f)["chapters"]

    return [
        Chapter(**item)
        for item in data
        if not filter_low_engagement
        or item.get("engagement_score", 0) >= ENGAGEMENT_THRESHOLD
    ]
