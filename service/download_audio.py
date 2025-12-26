from pathlib import Path
import yt_dlp
from domain.paths import Paths


def download_audio(
    youtube_url: str,
    quiet: bool = False,
) -> Path:
    """
    Downloads audio from a YouTube video as MP3.
    """
    audio_dir = Paths.get_audio_dir()

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(audio_dir / "%(id)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": quiet,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        video_id = info["id"]

    mp3_path = audio_dir / f"{video_id}.mp3"

    if not mp3_path.exists():
        raise RuntimeError("MP3 download failed")

    return mp3_path
