# Chapterize

An automated pipeline that converts YouTube videos into **short-form vertical (9:16) videos**.

The pipeline performs the following steps:

- Downloads audio and video from YouTube
- Generates **sentence-level and word-level** transcripts from audio
- Uses Gemini to split the transcript into **meaningful chapters**
- Filters chapters by engagement score
- Merges audio and video
- For each selected chapter:

  - Cuts a subclip
  - Crops the video to vertical (9:16)
  - Burns ASS subtitles into the video

- Outputs final short videos ready for publishing

---

## Requirements

- Python **3.12**
- `ffmpeg` and `ffprobe`
- `uv` ([https://docs.astral.sh/uv/](https://docs.astral.sh/uv/))
- Google Gemini API key

Required font:

- `assets/fonts/Montserrat-Black.ttf` (already under assets/fonts)

---

## Setup

```bash
uv python pin 3.12
uv sync
```

---

## Environment Variables

Copy the example file:

```bash
cp example.env .env
```

Fill in `.env`:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=GEMINI_3_FLASH
ENGAGEMENT_THRESHOLD=0.6
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
- Final shorts → `data/short`

---

## Output

For each generated short:

```
data/short/
├── {video_id}_{index}.mp4
├── {video_id}_{index}.txt   # chapter title
```

Subtitles:

```
data/subtitle/
├── {video_id}_{index}.ass
```

---

## Notes

- Subtitle font: **Montserrat Black (900)**
  Do not enable the `bold` flag.
- Video encoding is minimized; stream copy is used whenever possible.
- The entire pipeline orchestration lives in `run.py`.
