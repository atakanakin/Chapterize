from pathlib import Path
import yt_dlp
from domain.paths import Paths
from model.video_quality import VideoQuality


def download_video(
    youtube_url: str,
    quality: VideoQuality = VideoQuality.P1080,
    quiet: bool = False,
) -> Path:
    """
    Downloads a YouTube video with selectable max resolution.

    - Default: best video up to 1080p
    - Accepts higher fps variants (1080p50, 1080p60, etc.)
    """
    video_dir = Paths.get_video_dir()

    format_selector = f"bestvideo[height<={quality.max_height}]/best"

    ydl_opts = {
        "format": format_selector,
        "outtmpl": str(video_dir / "%(id)s.%(ext)s"),
        "merge_output_format": "mp4",
        "quiet": quiet,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        video_id = info["id"]

    output_path = next(video_dir.glob(f"{video_id}.*"), None)

    if not output_path or not output_path.exists():
        raise RuntimeError("Video download failed")

    return output_path
