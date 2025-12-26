from dataclasses import dataclass
from typing import Optional


@dataclass
class StreamerBBox:
    x: float
    y: float
    width: float
    height: float


@dataclass
class StreamerDetectionResult:
    is_reaction: bool
    confidence: float
    reason: str
    bounding_box: Optional[StreamerBBox] = None
