from domain.paths import Paths
from domain.audio import Audio
from domain.video import Video, VideoType
from service.download_audio import download_audio
from service.download_video import download_video


def run_pipeline(youtube_url: str) -> None:
    """
    Full pipeline to create shorts from a YouTube video.
    """
    lock_file = Paths.get_lock_file()
    if lock_file.exists():
        raise RuntimeError("Pipeline is already running. Lock file exists.")
    lock_file.touch()

    try:
        audio_file_path = download_audio(youtube_url)
        audio = Audio(audio_file_path)
        shorts = Audio.run_all(audio)

        video_file_path = download_video(youtube_url)
        video = Video(
            path=video_file_path,
            video_type=VideoType.WITHOUT_AUDIO,
        )
        video = video.add_audio(
            audio_file_path,
            output_path=Paths.get_video_dir() / f"{video_file_path.stem}.merged.mp4",
        )

        for short in shorts:
            subclip_path = (
                Paths.get_video_dir() / f"{short.subtitle_path.stem}_horizontal.mp4"
            )
            chapter = short.chapter
            subclip = video.extract_subclip(
                start_time=chapter.start,
                end_time=chapter.end,
                output_path=subclip_path,
            )
            cropped_subclip = subclip.smart_vertical_crop(
                output_path=Paths.get_video_dir() / f"{short.subtitle_path.stem}.mp4"
            )
            cropped_subclip.burn_in_subtitle(
                subtitle_path=short.subtitle_path,
                output_path=Paths.get_short_output_dir()
                / f"{short.subtitle_path.stem}.mp4",
            )
    finally:
        if lock_file.exists():
            lock_file.unlink()
