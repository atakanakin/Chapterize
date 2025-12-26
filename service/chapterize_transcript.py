from pathlib import Path
import json
from google import genai
from google.genai import types

from core.config import GEMINI_API_KEY, GEMINI_MODEL
from core.gemini import resolve_model
from domain.paths import Paths
from model.chapter import Chapter
from utils.llm_helper import extract_json, load_system_prompt


def load_transcript(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_chapters(
    transcript_path: Path,
    chapters_payload: dict,
) -> Path:
    """
    Writes chapter JSON to data/chapters using transcript base name.
    """
    chapter_dir = Paths.get_chapter_dir()
    chapter_file_name = f"{transcript_path.stem.split(".")[0]}.json"
    output_path = chapter_dir / chapter_file_name
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chapters_payload, f, ensure_ascii=False, indent=2)

    return output_path


def chapterize_transcript(
    transcript_path: Path,
) -> Path:
    """
    Runs Gemini chapterization and writes chapters JSON to disk.

    Returns:
        Path: written chapter file path
    """
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set")

    client = genai.Client(api_key=GEMINI_API_KEY)
    model = resolve_model(GEMINI_MODEL)

    system_prompt = load_system_prompt(Path("prompt/chapterize_system.md"))
    transcript = load_transcript(transcript_path)

    response = client.models.generate_content(
        model=model.value,
        contents=[
            system_prompt,
            json.dumps(transcript, ensure_ascii=False),
        ],
        config=types.GenerateContentConfig(
            temperature=0.4,
        ),
    )

    data = extract_json(response.text)

    chapters = [
        Chapter(
            title=c["title"],
            start=float(c["start"]),
            end=float(c["end"]),
            engagement_score=float(c["engagement_score"]),
        )
        for c in data["chapters"]
    ]

    payload = {
        "chapters": [
            {
                "title": ch.title,
                "start": ch.start,
                "end": ch.end,
                "engagement_score": ch.engagement_score,
            }
            for ch in chapters
        ]
    }

    output_path = write_chapters(
        transcript_path=transcript_path,
        chapters_payload=payload,
    )

    return output_path
