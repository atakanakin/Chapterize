from pathlib import Path
import subprocess


def burn_in_ass_subtitle(
    video_path: Path,
    subtitle_path: Path,
    output_path: Path,
    crf: int = 18,
    preset: str = "slow",
):
    """
    Burns ASS subtitles into video.

    - Video is re-encoded (required)
    - Audio is copied
    - Optimized for short-form quality
    """
    if not video_path.exists():
        raise FileNotFoundError(video_path)

    if not subtitle_path.exists():
        raise FileNotFoundError(subtitle_path)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-vf", f"ass={subtitle_path}:fontsdir=assets/fonts",
        "-c:v", "libx264",
        "-crf", str(crf),
        "-preset", preset,
        "-pix_fmt", "yuv420p",
        "-profile:v", "high",
        "-level", "4.2",
        "-movflags", "+faststart",
        "-c:a", "copy",
        str(output_path),
    ]

    subprocess.run(cmd, check=True)
