from pathlib import Path
from typing import Optional, Union, List
from model.short import Short
from model.transcript import TranscriptionMode
from model.chapter import Chapter
from service.transcribe_audio import transcribe_audio
from service.chapterize_transcript import chapterize_transcript
from service.generate_subtitle import generate_subtitle
from domain.paths import Paths
from utils.load_chapters import load_chapters


class Audio:
    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)
        self.chapters: Optional[List[Chapter]] = None
        self.shorts: List[Short] = []

        self._sentence_json_path: Optional[Path] = None
        self._word_json_path: Optional[Path] = None
        self._chapters_json_path: Optional[Path] = None

    def transcribe(
        self,
        mode: TranscriptionMode = TranscriptionMode.BOTH,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None,
    ):
        """
        Calls the transcription service.

        Args:
            mode: Transcription granularity.

        Returns:
            None
        """
        # Call external service
        # Note: transcribe_audio returns a list of Paths [path_sentence, path_word] depending on mode
        transcripts = transcribe_audio(
            audio_path=self.path,
            mode=mode,
            min_speakers=min_speakers,
            max_speakers=max_speakers,
        )
        for transcript_path in transcripts:
            if ".sentence." in transcript_path.name:
                self._sentence_json_path = transcript_path
            elif ".word." in transcript_path.name:
                self._word_json_path = transcript_path

        return

    def chapterize(self, filter_low_engagement: bool = True):
        """
        Generates chapters based on the existing sentence transcript.
        Requires transcribe() to be called first with SENTENCE or BOTH mode.
        """
        if not self._sentence_json_path or not self._sentence_json_path.exists():
            raise RuntimeError(
                "Sentence transcript not found. Call transcribe() first."
            )

        # Call external service
        self._chapters_json_path = chapterize_transcript(
            transcript_path=self._sentence_json_path
        )

        if not self._chapters_json_path or not self._chapters_json_path.exists():
            raise RuntimeError("Chapterization failed.")

        self.chapters = load_chapters(
            chapter_path=self._chapters_json_path,
            filter_low_engagement=filter_low_engagement,
        )

        return

    def generate_subtitles(self, write_titles: bool = True):
        """
        Generates subtitle files based on the existing chapters.
        Requires chapterize() to be called first.
        """
        if not self.chapters:
            raise RuntimeError("Chapters not found. Call chapterize() first.")

        shorts = []
        for i, ch in enumerate(self.chapters, start=1):
            subtitle_path = Paths.get_subtitle_dir() / f"{self.path.stem}_{i}.ass"
            title_path = Paths.get_short_output_dir() / f"{self.path.stem}_{i}.txt"
            if write_titles:
                title_path.write_text(ch.title.strip(), encoding="utf-8")
            generate_subtitle(
                word_transcript_path=self._word_json_path,
                output_path=subtitle_path,
                start=float(ch.start),
                end=float(ch.end),
            )
            short = Short(
                chapter=ch,
                subtitle_path=subtitle_path,
                title_text_path=title_path if write_titles else None,
            )
            shorts.append(short)

        self.shorts = shorts
        return

    def run_all(
        self,
        transcription_mode: TranscriptionMode = TranscriptionMode.BOTH,
        filter_low_engagement: bool = True,
        write_titles: bool = True,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None,
    ) -> List[Short]:
        """
        Runs the full pipeline: transcribe, chapterize, and generate subtitles.
        """
        self.transcribe(
            mode=transcription_mode,
            min_speakers=min_speakers,
            max_speakers=max_speakers,
        )
        self.chapterize(filter_low_engagement=filter_low_engagement)
        self.generate_subtitles(write_titles=write_titles)
        return self.shorts
