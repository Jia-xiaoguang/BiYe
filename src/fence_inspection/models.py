from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class TaskMeta:
    task_id: str
    drone_id: str
    area: str
    device_id: str
    operator: str
    started_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class Frame:
    frame_id: int
    timestamp: datetime
    blur_score: float
    payload: dict[str, Any]


@dataclass(slots=True)
class Detection:
    frame_id: int
    label: str
    confidence: float
    bbox: tuple[int, int, int, int]


@dataclass(slots=True)
class Track:
    track_id: int
    label: str
    bbox: tuple[int, int, int, int]
    frame_id: int


@dataclass(slots=True)
class Alert:
    task_id: str
    track_id: int
    label: str
    start_frame: int
    end_frame: int
    duration_frames: int
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class RuntimeConfig:
    enable_lsenet: bool = True
    detection_confidence_threshold: float = 0.5
    consistency_min_frames: int = 3
    alert_labels: tuple[str, ...] = ("fence_damage", "fence_missing", "intrusion")
