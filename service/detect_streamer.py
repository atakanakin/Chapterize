from pathlib import Path
from typing import List
from PIL import Image
from google import genai
from google.genai import types

from core.config import GEMINI_API_KEY, GEMINI_MODEL
from core.gemini import resolve_model
from model.streamer import StreamerBBox, StreamerDetectionResult
from utils.llm_helper import load_system_prompt, extract_json


def detect_streamer(frame_paths: List[Path]) -> StreamerDetectionResult:
    """
    Analyzes a list of video frames to detect if it's a reaction video
    and locates the streamer's bounding box.
    """
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set")

    if not frame_paths:
        raise ValueError("No frames provided for detection.")

    client = genai.Client(api_key=GEMINI_API_KEY)
    model = resolve_model(GEMINI_MODEL)
    system_prompt = load_system_prompt(Path("prompt/streamer_detection_system.md"))

    images = []
    for p in frame_paths:
        if not p.exists():
            continue
        try:
            img = Image.open(p)
            images.append(img)
        except Exception as e:
            print(f"Warning: Could not load frame {p}: {e}")

    if not images:
        raise RuntimeError("No valid images could be loaded from the provided paths.")

    contents = [system_prompt]
    contents.extend(images)

    response = client.models.generate_content(
        model=model.value,
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )

    data = extract_json(response.text)

    bbox_data = data.get("streamer_bbox")
    bbox = None

    if bbox_data:
        bbox = StreamerBBox(
            x=float(bbox_data["x"]),
            y=float(bbox_data["y"]),
            width=float(bbox_data["width"]),
            height=float(bbox_data["height"]),
        )

    return StreamerDetectionResult(
        is_reaction=data["is_reaction"],
        confidence=float(data["confidence"]),
        reason=data["reason"],
        bounding_box=bbox,
    )
