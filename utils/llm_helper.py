import json
from pathlib import Path


def extract_json(text: str) -> dict:
    """
    Safely extract JSON from Gemini response.
    Handles ```json``` fenced outputs.
    """
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1].strip()
    return json.loads(text)


def load_system_prompt(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")
