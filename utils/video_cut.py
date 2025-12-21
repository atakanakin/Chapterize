from pathlib import Path
import subprocess


def cut_subclip(
    video_path: Path,
    start: float,
    end: float,
    output_path: Path,
):
    cmd = [
        "ffmpeg",
        "-y",
        "-ss", str(start),
        "-to", str(end),
        "-i", str(video_path),
        "-c", "copy",
        str(output_path),
    ]

    subprocess.run(cmd, check=True)
