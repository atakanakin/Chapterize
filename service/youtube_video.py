from pathlib import Path
import yt_dlp

from core.video import VideoQuality
from core.paths import get_video_dir


def download_video(
    youtube_url: str,
    quality: VideoQuality = VideoQuality.P1080,
    output_base_dir: Path | None = None,
    quiet: bool = False,
) -> Path:
    """
    Downloads a YouTube video with selectable max resolution.

    - Default: best video up to 1080p
    - Accepts higher fps variants (1080p50, 1080p60, etc.)
    """
    video_dir = get_video_dir(output_base_dir)

    # 🔥 yt-dlp format selector
    format_selector = (
        f"bestvideo[height<={quality.max_height}]/best"
    )

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
