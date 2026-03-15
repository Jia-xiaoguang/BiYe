from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, Iterator

from fence_inspection.models import Frame


@dataclass(slots=True)
class VideoStreamAdapter:
    """实时视频流接入适配器（原型版：使用可迭代数据源模拟）。"""

    stream_name: str
    values: Iterable[dict]

    def frames(self) -> Iterator[Frame]:
        now = datetime.utcnow()
        for idx, payload in enumerate(self.values):
            blur = float(payload.get("blur_score", 0.0))
            yield Frame(
                frame_id=idx,
                timestamp=now + timedelta(milliseconds=40 * idx),
                blur_score=blur,
                payload=payload,
            )


@dataclass(slots=True)
class LocalVideoImporter:
    """离线视频导入模块（原型版：使用列表帧数据模拟离线文件）。"""

    file_path: str
    frames_payload: list[dict]

    def frames(self) -> Iterator[Frame]:
        adapter = VideoStreamAdapter(stream_name=self.file_path, values=self.frames_payload)
        yield from adapter.frames()
