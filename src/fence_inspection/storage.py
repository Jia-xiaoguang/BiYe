from __future__ import annotations

from dataclasses import dataclass, field

from fence_inspection.models import Alert, Detection, Frame, TaskMeta, Track


@dataclass(slots=True)
class InMemoryRepository:
    tasks: dict[str, TaskMeta] = field(default_factory=dict)
    frames: dict[str, list[Frame]] = field(default_factory=dict)
    detections: dict[str, list[Detection]] = field(default_factory=dict)
    tracks: dict[str, list[Track]] = field(default_factory=dict)
    alerts: dict[str, list[Alert]] = field(default_factory=dict)

    def save_task(self, task: TaskMeta) -> None:
        self.tasks[task.task_id] = task
        self.frames.setdefault(task.task_id, [])
        self.detections.setdefault(task.task_id, [])
        self.tracks.setdefault(task.task_id, [])
        self.alerts.setdefault(task.task_id, [])

    def save_frame(self, task_id: str, frame: Frame) -> None:
        self.frames[task_id].append(frame)

    def save_detections(self, task_id: str, detections: list[Detection]) -> None:
        self.detections[task_id].extend(detections)

    def save_tracks(self, task_id: str, tracks: list[Track]) -> None:
        self.tracks[task_id].extend(tracks)

    def save_alert(self, task_id: str, alert: Alert) -> None:
        self.alerts[task_id].append(alert)
