# Chapterize

An automated pipeline that converts YouTube videos into **short-form vertical (9:16) videos** with **smart framing** and **multi-speaker subtitles**.

The pipeline performs the following steps:

- **Download:** Fetches high-quality audio and video from YouTube.
- **Advanced Transcription:**
  - Uses `faster-whisper` for natural, high-accuracy timing.
  - Performs **Speaker Diarization** using `whisperx` to identify who is speaking.
- **Content Analysis:** Uses Gemini to split the transcript into **meaningful chapters** and filters them by engagement score.
- **Smart Video Processing:**
  - **Streamer Detection:** Automatically detects facecams/bounding boxes.
  - **Dynamic Layout:**
    - If a streamer is detected: Applies a **Split-Screen** layout (Streamer Top / Content Bottom).
    - If no streamer is detected: Applies a standard **Center Crop**.
- **Dynamic Subtitles:**
  - Burns ASS subtitles into the video.
  - Applies **Contextual Coloring** to speakers based on talk-time rank (e.g., Main Speaker = White, Secondary = Gold).
- **Production:** Outputs final short videos ready for publishing.

## Additional Features

- **Lock Mechanism**: Ensures only one instance of the pipeline runs at a time by creating a lock file in the data directory. If a lock file exists, the pipeline raises an error to prevent conflicts.
- **Automatic Cleanup**: Before starting, the pipeline checks for the lock file. If absent, it cleans all files and subdirectories in the data directory to ensure a fresh start.
- **Final Output Directory**: After processing, all generated short videos are moved from the internal shorts directory to a `final` directory located in the parent folder of the working directory, keeping outputs organized and accessible.

---

## Requirements

- Python **3.12**
- `ffmpeg` and `ffprobe`
- `uv` ([https://docs.astral.sh/uv/](https://docs.astral.sh/uv/))
- **Google Gemini API Key** (for summarization)
- **Hugging Face Token** (Required for Speaker Diarization models)

Required font:

- `assets/fonts/Montserrat-Black.ttf` (already under assets/fonts)

---

## Setup

1. **Install Dependencies:**

   ```bash
   uv python pin 3.12
   uv sync
   ```

2. **Hugging Face Permissions (Important):**
   You must accept the user conditions for the following models on Hugging Face to use Diarization:

- [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
- [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)

---

## Environment Variables

Copy the example file:

```bash
cp example.env .env
```

Fill in `.env`:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-2.0-flash-exp
ENGAGEMENT_THRESHOLD=0.6

# Required for WhisperX / Pyannote Diarization
HF_TOKEN=hf_YourHuggingFaceTokenHere
```

---

## Run

```bash
uv run main.py
```

Default output directories:

- Audio → `data/audio`
- Transcript → `data/transcript`
- Chapter → `data/chapter`
- Subtitle → `data/subtitle`
- Video → `data/video`
- Intermediate shorts → `data/short` (moved to final directory after processing)

---

## Subtitle Styling

The pipeline uses a **Contextual Ranking System** to assign colors. It calculates who speaks the most in a specific clip and assigns colors from a priority palette:

1. **Rank 1 (Main Speaker):** White (`&H20FFFFFF`)
2. **Rank 2 (Secondary):** Gold / Amber (`&H2032C9FF`)
3. **Rank 3 (Tertiary):** Pastel Red (`&H206060FF`)
4. **Rank 4 (Quaternary):** Sky Blue (`&H20FFC080`)

_Font:_ Montserrat Black (900).

---

## Output

For each generated short:

```
../final/ (parent directory of working directory)
├── {video_id}_{index}.mp4
├── {video_id}_{index}.txt   # chapter title
```

Intermediate files are stored in `data/` subdirectories and cleaned up after processing.

---

## Notes

- **Hybrid Transcriber:** The project uses a custom hybrid approach. `faster-whisper` is used for ASR (Text & Timing) to ensure natural flow, while `whisperx` is injected solely for Speaker Identification.
- **PyTorch 2.6+:** The codebase includes patches to handle security restrictions in newer PyTorch versions regarding model loading.
- **Orchestration:** The entire pipeline logic lives in `run.py`.
