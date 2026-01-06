# Chapterize

An automated pipeline that converts YouTube videos into **short-form vertical (9:16) videos** with **smart framing** and **multi-speaker subtitles**. The pipeline integrates with **Modal** for cloud-based transcription and video rendering to ensure high performance and scalability.

The pipeline performs the following steps:

- **Download:** Fetches high-quality audio and video from YouTube.
- **Advanced Transcription:** Uses cloud-deployed Whisper models for natural, high-accuracy timing and Speaker Diarization.
- **Content Analysis:** Uses Gemini to split the transcript into **meaningful chapters** and filters them by engagement score.
- **Smart Video Processing:**
  - **Streamer Detection:** Automatically detects facecams/bounding boxes.
  - **Dynamic Layout:**
    - If a streamer is detected: Applies a **Split-Screen** layout (Streamer Top / Content Bottom).
    - If no streamer is detected: Applies a standard **Center Crop**.
- **Dynamic Subtitles:**
  - Burns ASS subtitles into the video using cloud rendering.
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
- **Modal Account** (for cloud-based transcription and video rendering)
- **Google Gemini API Key** (for summarization)

Required font:

- `assets/fonts/Montserrat-Black.ttf` (already under assets/fonts)

---

## Setup

1. **Install Dependencies:**

   ```bash
   uv python pin 3.12
   uv sync
   ```

2. **Install Modal CLI:**

   ```bash
   uv add modal
   ```

3. **Authenticate with Modal:**

   ```bash
    uv run modal setup
   ```

   Follow the prompts to authenticate your Modal account.

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
```

---

## Run

The pipeline runs locally but leverages Modal for GPU-accelerated transcription and video rendering.

```bash
uv run main.py
```

The pipeline will automatically connect to the deployed Modal apps (`whisper-diarizer-prod` for transcription and `video-renderer-prod` for rendering) to perform the heavy computations in the cloud.

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

- **Cloud-Based Processing:** Transcription and video rendering are performed on Modal's cloud infrastructure for better performance and scalability.
- **Hybrid Transcriber:** The project uses a custom hybrid approach. Transcription is handled by Modal-deployed Whisper models for ASR and Speaker Diarization.
- **Orchestration:** The entire pipeline logic lives in `run.py`.
