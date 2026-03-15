from __future__ import annotations

from dataclasses import dataclass

from fence_inspection.models import Frame


@dataclass(slots=True)
class LSENetEnhancer:
    """LSENet 去模糊增强模块（工程占位实现）。"""

    strength: float = 0.6

    def enhance(self, frame: Frame) -> Frame:
        # 用 blur_score 的下降模拟去模糊后的清晰度提升。
        restored_blur = max(0.0, frame.blur_score * (1 - self.strength))
        enhanced_payload = dict(frame.payload)
        enhanced_payload["enhanced"] = True
        enhanced_payload["original_blur_score"] = frame.blur_score
        return Frame(
            frame_id=frame.frame_id,
            timestamp=frame.timestamp,
            blur_score=restored_blur,
            payload=enhanced_payload,
        )
