import subprocess
import random
import json
from pathlib import Path
from typing import List

from domain.paths import Paths


def get_video_duration(video_path: Path) -> float:
    """Helper to get exact video duration in seconds."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])


def extract_frames(video_path: Path, frame_count: int = 1) -> List[Path]:
    """
    Extracts random frames from the middle 60% of the video.

    Args:
        video_path: Source video file.
        frame_count: Number of frames to extract (default 1).

    Returns:
        List[Path]: List of paths to the saved PNG images.
    """
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    video_name = video_path.stem
    output_dir = Paths.get_frame_dir()

    duration = get_video_duration(video_path)

    # Define Safe Zone (Avoid first 20% and last 20%)
    safe_start = duration * 0.2
    safe_end = duration * 0.8

    if safe_end <= safe_start:
        # Fallback for very short videos: use middle point
        safe_start = 0.0
        safe_end = duration

    extracted_paths = []

    for i in range(frame_count):
        random_time = random.uniform(safe_start, safe_end)
        output_filename = f"{video_name}_{i+1}.png"
        output_path = output_dir / output_filename

        # Extract Frame using FFmpeg
        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            str(random_time),
            "-i",
            str(video_path),
            "-vframes",
            "1",
            "-q:v",
            "2",
            str(output_path),
        ]
        subprocess.run(cmd, check=True, capture_output=True)

        extracted_paths.append(output_path)

    return extracted_paths
