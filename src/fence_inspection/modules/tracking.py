from __future__ import annotations

from dataclasses import dataclass, field

from fence_inspection.models import Detection, Track


def _center(bbox: tuple[int, int, int, int]) -> tuple[float, float]:
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)


@dataclass(slots=True)
class DeepSORTTracker:
    """DeepSORT 轨迹一致性验证模块（轻量替代实现）。"""

    max_center_distance: float = 25.0
    _next_track_id: int = 1
    _tracks: dict[int, Track] = field(default_factory=dict)

    def update(self, detections: list[Detection]) -> list[Track]:
        updated: list[Track] = []
        for det in detections:
            track_id = self._match(det)
            track = Track(
                track_id=track_id,
                label=det.label,
                bbox=det.bbox,
                frame_id=det.frame_id,
            )
            self._tracks[track_id] = track
            updated.append(track)
        return updated

    def _match(self, detection: Detection) -> int:
        det_center = _center(detection.bbox)
        best_id = None
        best_dist = self.max_center_distance

        for tid, track in self._tracks.items():
            if track.label != detection.label:
                continue
            tr_center = _center(track.bbox)
            dist = ((det_center[0] - tr_center[0]) ** 2 + (det_center[1] - tr_center[1]) ** 2) ** 0.5
            if dist <= best_dist:
                best_dist = dist
                best_id = tid

        if best_id is not None:
            return best_id

        tid = self._next_track_id
        self._next_track_id += 1
        return tid


@dataclass(slots=True)
class ConsistencyValidator:
    min_frames: int = 3
    _track_lengths: dict[int, int] = field(default_factory=dict)

    def push(self, tracks: list[Track]) -> list[Track]:
        confirmed: list[Track] = []
        for track in tracks:
            length = self._track_lengths.get(track.track_id, 0) + 1
            self._track_lengths[track.track_id] = length
            if length >= self.min_frames:
                confirmed.append(track)
        return confirmed

    def duration(self, track_id: int) -> int:
        return self._track_lengths.get(track_id, 0)
