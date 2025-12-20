import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DATA_DIR = Path("data")

AUDIO_DIR_NAME = "audio"
TRANSCRIPT_DIR_NAME = "transcripts"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "FLASH")