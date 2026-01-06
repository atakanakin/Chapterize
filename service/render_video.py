import modal
import time
from pathlib import Path
from typing import Optional
from model.streamer import StreamerBBox
from domain.paths import Paths


def render_video(
    video_path: Path,
    subtitle_path: Path,
    output_path: Path,
    bbox: Optional[StreamerBBox] = None,
    fonts_dir: Path = Paths.get_font_dir(),
) -> Path:
    """
    Connects to deployed 'video-renderer-prod', executes pipeline, and saves result locally.
    """
    print(f"-> Connecting to Modal: video-renderer-prod...")
    RendererRemote = modal.Cls.from_name("video-renderer-prod", "VideoRenderer")
    renderer = RendererRemote()

    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")
    if not subtitle_path.exists():
        raise FileNotFoundError(f"Subtitle not found: {subtitle_path}")

    with open(video_path, "rb") as f:
        v_data = f.read()
    with open(subtitle_path, "rb") as f:
        s_data = f.read()

    font_files = {}
    if fonts_dir.exists():
        for f in fonts_dir.glob("*.[to]tf"):
            with open(f, "rb") as font_f:
                font_files[f.name] = font_f.read()

    print("-> Uploading and Rendering...")
    start_time = time.time()

    try:
        result_bytes = renderer.render_pipeline.remote(
            video_bytes=v_data, subtitle_bytes=s_data, font_files=font_files, bbox=bbox
        )
    except Exception as e:
        print(f"Remote Error: {e}")
        raise e

    duration = time.time() - start_time
    print(f"-> Finished in {duration:.2f}s")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(result_bytes)

    return output_path
