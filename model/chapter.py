from dataclasses import dataclass


@dataclass
class Chapter:
    title: str
    start: float
    end: float
    engagement_score: float
