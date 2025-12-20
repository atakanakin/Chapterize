from pathlib import Path
import json

from core.paths import get_chapter_dir


def write_chapters(
    transcript_path: Path,
    chapters_payload: dict,
    output_base_dir: Path | None = None,
) -> Path:
    """
    Writes chapter JSON to data/chapters using transcript base name.
    """
    chapter_dir = get_chapter_dir(output_base_dir)
    output_path = chapter_dir / f"{transcript_path.stem}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chapters_payload, f, ensure_ascii=False, indent=2)

    return output_path
