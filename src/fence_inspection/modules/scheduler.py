from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from fence_inspection.models import Frame


@dataclass(slots=True)
class VideoScheduler:
    """视频解析与调度模块：统一实时与离线帧输入，进行帧率抽样。"""

    target_fps: int = 25

    def schedule(self, frames: Iterator[Frame], source_fps: int = 25) -> Iterator[Frame]:
        if self.target_fps <= 0:
            raise ValueError("target_fps must be positive")

        step = max(1, round(source_fps / self.target_fps))
        for idx, frame in enumerate(frames):
            if idx % step == 0:
                yield frame
