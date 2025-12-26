from pathlib import Path
import json
from faster_whisper import WhisperModel

from model.transcript import TranscriptionMode
from domain.paths import Paths

_MODEL = WhisperModel(
    "medium",
    compute_type="int8",
)


def transcribe_audio(
    audio_path: Path,
    mode: TranscriptionMode = TranscriptionMode.BOTH,
) -> list[Path]:
    """Transcribes the given audio file and writes transcripts to JSON files.
    Returns:
        list[Path]: written transcript file paths
    """
    if not audio_path.exists():
        raise FileNotFoundError(audio_path)

    transcript_dir = Paths.get_transcript_dir()

    written_files: list[Path] = []

    segments, info = _MODEL.transcribe(
        str(audio_path),
        vad_filter=True,
        beam_size=5,
        word_timestamps=(mode != TranscriptionMode.SENTENCE),
    )
    segments = list(segments)

    # ---------- SENTENCE ----------
    if mode in (TranscriptionMode.SENTENCE, TranscriptionMode.BOTH):
        sentence_path = transcript_dir / f"{audio_path.stem}.sentence.json"

        sentence_payload = {
            "language": info.language,
            "mode": "sentence",
            "segments": [
                {
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text.strip(),
                }
                for seg in segments
            ],
        }

        with open(sentence_path, "w", encoding="utf-8") as f:
            json.dump(sentence_payload, f, ensure_ascii=False, indent=2)

        written_files.append(sentence_path)

    # ---------- WORD ----------
    if mode in (TranscriptionMode.WORD, TranscriptionMode.BOTH):
        word_path = transcript_dir / f"{audio_path.stem}.word.json"

        words = []
        for seg in segments:
            if not seg.words:
                continue
            for w in seg.words:
                words.append(
                    {
                        "start": w.start,
                        "end": w.end,
                        "text": w.word.strip(),
                    }
                )

        word_payload = {
            "language": info.language,
            "mode": "word",
            "words": words,
        }

        with open(word_path, "w", encoding="utf-8") as f:
            json.dump(word_payload, f, ensure_ascii=False, indent=2)

        written_files.append(word_path)

    return written_files
