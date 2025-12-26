from enum import Enum


class VideoQuality(Enum):
    P480 = 480
    P720 = 720
    P1080 = 1080
    P1440 = 1440
    P2160 = 2160  # 4K

    @property
    def max_height(self) -> int:
        return self.value
