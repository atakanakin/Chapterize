from pathlib import Path
import subprocess


def merge_video_audio(
    video_path: Path,
    audio_path: Path,
    output_path: Path,
):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        str(output_path),
    ]

    subprocess.run(cmd, check=True)
