import modal
import json
import time
from pathlib import Path
from typing import Optional, List
from domain.paths import Paths


def _transfer_sentence_json(input_json: dict) -> dict:
    return {
        "language": input_json["meta"]["language"],
        "mode": "sentence",
        "segments": input_json["sentence"],
    }


def _transfer_word_json(input_json: dict) -> dict:
    return {
        "language": input_json["meta"]["language"],
        "mode": "word",
        "words": input_json["word"],
    }


def transcribe_audio(
    audio_path: Path,
    min_speakers: Optional[int] = None,
    max_speakers: Optional[int] = None,
) -> List[Path]:
    """
    Connects to the deployed Modal app, sends audio, and saves the JSON result.
    """
    # Connect to the deployed App
    print(f"-> Connecting to Modal App: whisper-diarizer-prod...")
    # Matches the app_name and class_name in your main.py
    TranscriberRemote = modal.Cls.from_name("whisper-diarizer-prod", "AudioTranscriber")
    transcriber = TranscriberRemote()
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print(
        f"-> Reading local file: {audio_path.name} ({audio_path.stat().st_size / 1024 / 1024:.2f} MB)"
    )
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    # Remote Execution (The Magic Part)
    print("-> Sending to GPU... (Waiting for response)")
    start_time = time.time()

    # .remote() sends the request to the cloud
    result = transcriber.process_audio.remote(
        audio_bytes=audio_bytes,
        min_speakers=min_speakers,
        max_speakers=max_speakers,
    )

    duration = time.time() - start_time
    print(f"-> Completed in {duration:.2f} seconds!")

    transcript_dir = Paths.get_transcript_dir()
    written_files: list[Path] = []

    sentence_path = transcript_dir / f"{audio_path.stem}.sentence.json"
    word_path = transcript_dir / f"{audio_path.stem}.word.json"

    print(f"-> Writing sentence-level JSON to: {sentence_path}")
    sentence_json = _transfer_sentence_json(result)
    with open(sentence_path, "w", encoding="utf-8") as f:
        json.dump(sentence_json, f, ensure_ascii=False, indent=2)
    written_files.append(sentence_path)
    print(f"-> Writing word-level JSON to: {word_path}")
    word_json = _transfer_word_json(result)
    with open(word_path, "w", encoding="utf-8") as f:
        json.dump(word_json, f, ensure_ascii=False, indent=2)
    written_files.append(word_path)
    print(f"-> Written files: {[str(p) for p in written_files]}")

    return written_files
