import torch
import functools
import json
import gc
from pathlib import Path
from typing import Optional

# Core ASR Library
from faster_whisper import WhisperModel

from model.transcript import TranscriptionMode
from domain.paths import Paths
from core.config import HF_TOKEN

# --- FIX: PyTorch 2.6+ Security Patch (Required for WhisperX/Pyannote) ---
_original_load = torch.load


@functools.wraps(_original_load)
def _hack_torch_load(*args, **kwargs):
    kwargs["weights_only"] = False
    return _original_load(*args, **kwargs)


torch.load = _hack_torch_load
# -------------------------------------------------------------------------

# --- GLOBAL CONFIGURATION ---
if torch.cuda.is_available():
    DEVICE = "cuda"
    COMPUTE_TYPE = "int8"
else:
    DEVICE = "cpu"
    COMPUTE_TYPE = "int8"

# Global model instance (Singleton pattern)
_ASR_MODEL: Optional[WhisperModel] = None


def get_asr_model(model: str = "medium") -> WhisperModel:
    """Loads the ASR model once and returns the global instance."""
    global _ASR_MODEL
    if _ASR_MODEL is None:
        print(f"-> Loading faster-whisper Model ({DEVICE})...")
        _ASR_MODEL = WhisperModel(model, device=DEVICE, compute_type=COMPUTE_TYPE)
    return _ASR_MODEL


def transcribe_audio(
    audio_path: Path,
    mode: TranscriptionMode = TranscriptionMode.BOTH,
    speaker_diarization: bool = True,
    min_speakers: Optional[int] = None,
    max_speakers: Optional[int] = None,
) -> list[Path]:
    """
    Transcribes audio using 'faster-whisper'.
    Optionally performs Speaker Diarization using 'whisperx'.

    Args:
        audio_path: Path to the input audio file.
        mode: Output mode (SENTENCE, WORD, or BOTH).
        speaker_diarization: If True, uses WhisperX to identify speakers.
    """
    if not audio_path.exists():
        raise FileNotFoundError(audio_path)

    transcript_dir = Paths.get_transcript_dir()
    written_files: list[Path] = []
    audio_file = str(audio_path)

    # 1. TRANSCRIPTION (ASR)
    # Uses the global cached model for performance
    model = get_asr_model()

    print("-> Transcribing (Natural Timing)...")
    segments_gen, info = model.transcribe(
        audio_file,
        vad_filter=True,
        beam_size=5,
        word_timestamps=(mode != TranscriptionMode.SENTENCE),
    )

    raw_segments = list(segments_gen)
    model_lang = info.language

    # 2. DATA NORMALIZATION
    # Convert faster-whisper segments to a format WhisperX accepts (and for uniform output)
    formatted_segments = []
    for seg in raw_segments:
        wx_seg = {"start": seg.start, "end": seg.end, "text": seg.text, "words": []}
        if seg.words:
            for w in seg.words:
                wx_seg["words"].append(
                    {
                        "start": w.start,
                        "end": w.end,
                        "word": w.word,
                        "score": w.probability,
                        # Default speaker if diarization is skipped
                        "speaker": "SPEAKER_00",
                    }
                )
        formatted_segments.append(wx_seg)

    transcript_result = {"segments": formatted_segments, "language": model_lang}

    # 3. SPEAKER DIARIZATION (Optional)
    if speaker_diarization:
        if not HF_TOKEN:
            raise ValueError("HF_TOKEN is missing in .env for Diarization")

        print("-> Diarizing (Finding Speakers)...")

        # Late import to save resources if not needed
        import whisperx.diarize

        # Perform Diarization
        diarize_model = whisperx.diarize.DiarizationPipeline(
            use_auth_token=HF_TOKEN, device=DEVICE
        )
        diarize_segments = diarize_model(
            audio_file, min_speakers=min_speakers, max_speakers=max_speakers
        )

        # Merge Speaker IDs with Word Timestamps
        # This updates 'transcript_result' in-place
        transcript_result = whisperx.diarize.assign_word_speakers(
            diarize_segments, transcript_result
        )

        # Cleanup Diarization model to free VRAM
        del diarize_model
        gc.collect()
        if DEVICE == "cuda":
            torch.cuda.empty_cache()

    # --- WRITE OUTPUTS ---
    final_segments = transcript_result["segments"]

    # ---------- SENTENCE ----------
    if mode in (TranscriptionMode.SENTENCE, TranscriptionMode.BOTH):
        sentence_path = transcript_dir / f"{audio_path.stem}.sentence.json"

        output_segments = []
        for seg in final_segments:
            output_segments.append(
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"].strip(),
                    "speaker": seg.get("speaker", "SPEAKER_00"),
                }
            )

        payload = {
            "language": model_lang,
            "mode": "sentence",
            "segments": output_segments,
        }

        with open(sentence_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        written_files.append(sentence_path)

    # ---------- WORD ----------
    if mode in (TranscriptionMode.WORD, TranscriptionMode.BOTH):
        word_path = transcript_dir / f"{audio_path.stem}.word.json"

        all_words = []
        for seg in final_segments:
            seg_speaker = seg.get("speaker", "SPEAKER_00")

            # 'words' key is guaranteed by our normalization step
            if "words" in seg:
                for w in seg["words"]:
                    all_words.append(
                        {
                            "start": w["start"],
                            "end": w["end"],
                            "text": w["word"].strip(),
                            # Word-level speaker or fallback to segment speaker
                            "speaker": w.get("speaker", seg_speaker),
                        }
                    )

        payload = {
            "language": model_lang,
            "mode": "word",
            "words": all_words,
        }

        with open(word_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        written_files.append(word_path)

    return written_files
