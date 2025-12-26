import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DATA_DIR = Path("data")
AUDIO_DIR = "audio"
TRANSCRIPT_DIR = "transcript"
CHAPTER_DIR = "chapter"
VIDEO_DIR = "video"
FRAME_DIR = "frame"
SUBTITLE_DIR = "subtitle"
SHORT_DIR = "short"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "GEMINI_3_FLASH")
HF_TOKEN = os.getenv("HF_TOKEN")

ENGAGEMENT_THRESHOLD = float(os.getenv("ENGAGEMENT_THRESHOLD", "0.65"))
