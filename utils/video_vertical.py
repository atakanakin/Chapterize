from pathlib import Path
import subprocess
import json


def get_video_resolution(video_path: Path) -> tuple[int, int]:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json",
        str(video_path),
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, check=True
    )
    info = json.loads(result.stdout)
    stream = info["streams"][0]
    return stream["width"], stream["height"]


def crop_to_vertical(
    input_path: Path,
    output_path: Path,
):
    width, height = get_video_resolution(input_path)

    target_ratio = 9 / 16
    current_ratio = width / height

    # Already vertical or square-ish
    if current_ratio <= target_ratio:
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(input_path),
            "-vf", "scale=1080:1920",
            "-c:a", "copy",
            str(output_path),
        ]
    else:
        crop_width = int(height * target_ratio)
        x_offset = int((width - crop_width) / 2)

        vf = (
            f"crop={crop_width}:{height}:{x_offset}:0,"
            f"scale=1080:1920"
        )

        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(input_path),
            "-vf", vf,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "copy",
            str(output_path),
        ]

    subprocess.run(cmd, check=True)
