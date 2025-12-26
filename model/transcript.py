from dataclasses import dataclass
from enum import Enum
from typing import List


class TranscriptionMode(Enum):
    SENTENCE = "sentence"
    WORD = "word"
    BOTH = "both"


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass
class Transcript:
    mode: TranscriptionMode
    language: str
    segments: List[TranscriptSegment]
