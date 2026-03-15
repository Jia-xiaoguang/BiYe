from __future__ import annotations

from dataclasses import dataclass, field
from random import Random

from fence_inspection.models import Detection, Frame


@dataclass(slots=True)
class FADYOLOv11Detector:
    """FAD-YOLOv11 异常检测模块（原型规则实现，可替换为真实模型推理）。"""

    seed: int = 7
    _rng: Random = field(init=False)

    def __post_init__(self) -> None:
        self._rng = Random(self.seed)

    def detect(self, frame: Frame) -> list[Detection]:
        anomalies = frame.payload.get("anomalies", [])
        detections: list[Detection] = []
        for item in anomalies:
            label = item["label"]
            confidence = float(item.get("confidence", self._rng.uniform(0.4, 0.95)))
            bbox = tuple(item.get("bbox", (10, 10, 80, 80)))
            detections.append(
                Detection(
                    frame_id=frame.frame_id,
                    label=label,
                    confidence=confidence,
                    bbox=bbox,
                )
            )
        return detections
