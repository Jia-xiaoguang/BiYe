from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, Iterator

from fence_inspection.models import Alert, RuntimeConfig, TaskMeta
from fence_inspection.modules.acquisition import LocalVideoImporter, VideoStreamAdapter
from fence_inspection.modules.detection import FADYOLOv11Detector
from fence_inspection.modules.enhancement import LSENetEnhancer
from fence_inspection.modules.scheduler import VideoScheduler
from fence_inspection.modules.tracking import ConsistencyValidator, DeepSORTTracker
from fence_inspection.storage import InMemoryRepository


@dataclass(slots=True)
class InspectionSystem:
    repository: InMemoryRepository
    config: RuntimeConfig = field(default_factory=RuntimeConfig)

    scheduler: VideoScheduler = field(init=False)
    enhancer: LSENetEnhancer = field(init=False)
    detector: FADYOLOv11Detector = field(init=False)
    tracker: DeepSORTTracker = field(init=False)
    validator: ConsistencyValidator = field(init=False)

    def __post_init__(self) -> None:
        self.scheduler = VideoScheduler(target_fps=20)
        self.enhancer = LSENetEnhancer()
        self.detector = FADYOLOv11Detector()
        self.tracker = DeepSORTTracker()
        self.validator = ConsistencyValidator(min_frames=self.config.consistency_min_frames)

    def create_task(self, task_id: str, drone_id: str, area: str, device_id: str, operator: str) -> TaskMeta:
        task = TaskMeta(
            task_id=task_id,
            drone_id=drone_id,
            area=area,
            device_id=device_id,
            operator=operator,
        )
        self.repository.save_task(task)
        return task

    def run_offline(self, task_id: str, file_path: str, frames_payload: list[dict]) -> list[Alert]:
        importer = LocalVideoImporter(file_path=file_path, frames_payload=frames_payload)
        return self._run(task_id, importer.frames())

    def run_realtime(self, task_id: str, stream_name: str, values: Iterable[dict]) -> list[Alert]:
        adapter = VideoStreamAdapter(stream_name=stream_name, values=values)
        return self._run(task_id, adapter.frames())

    def _run(self, task_id: str, frames_iter: Iterator) -> list[Alert]:
        for frame in self.scheduler.schedule(frames_iter, source_fps=25):
            if self.config.enable_lsenet:
                frame = self.enhancer.enhance(frame)

            self.repository.save_frame(task_id, frame)

            detections = [
                d
                for d in self.detector.detect(frame)
                if d.confidence >= self.config.detection_confidence_threshold
            ]
            self.repository.save_detections(task_id, detections)

            tracks = self.tracker.update(detections)
            self.repository.save_tracks(task_id, tracks)

            confirmed = self.validator.push(tracks)
            self._emit_alerts(task_id, confirmed)

        return self.repository.alerts[task_id]

    def _emit_alerts(self, task_id: str, confirmed_tracks) -> None:
        existing = {(a.track_id, a.end_frame) for a in self.repository.alerts[task_id]}
        for track in confirmed_tracks:
            if track.label not in self.config.alert_labels:
                continue
            duration = self.validator.duration(track.track_id)
            key = (track.track_id, track.frame_id)
            if key in existing:
                continue
            alert = Alert(
                task_id=task_id,
                track_id=track.track_id,
                label=track.label,
                start_frame=max(0, track.frame_id - duration + 1),
                end_frame=track.frame_id,
                duration_frames=duration,
                created_at=datetime.utcnow(),
            )
            self.repository.save_alert(task_id, alert)
