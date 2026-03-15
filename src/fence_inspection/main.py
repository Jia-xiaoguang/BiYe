from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from fence_inspection import InMemoryRepository, InspectionSystem


def demo_payload() -> list[dict]:
    return [
        {"blur_score": 0.8, "anomalies": []},
        {
            "blur_score": 0.7,
            "anomalies": [{"label": "fence_damage", "confidence": 0.88, "bbox": (20, 20, 70, 70)}],
        },
        {
            "blur_score": 0.6,
            "anomalies": [{"label": "fence_damage", "confidence": 0.9, "bbox": (22, 22, 72, 72)}],
        },
        {
            "blur_score": 0.65,
            "anomalies": [{"label": "fence_damage", "confidence": 0.92, "bbox": (24, 22, 74, 74)}],
        },
    ]


def main() -> None:
    repo = InMemoryRepository()
    system = InspectionSystem(repository=repo)

    task = system.create_task(
        task_id="task-001",
        drone_id="drone-A1",
        area="zone-east",
        device_id="cam-01",
        operator="admin",
    )
    alerts = system.run_offline(task.task_id, "demo.mp4", demo_payload())

    output = {
        "task_id": task.task_id,
        "alerts": [asdict(a) for a in alerts],
        "total_frames": len(repo.frames[task.task_id]),
        "total_detections": len(repo.detections[task.task_id]),
        "total_tracks": len(repo.tracks[task.task_id]),
    }

    out_path = Path("run_result.json")
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"done, result written to {out_path}")


if __name__ == "__main__":
    main()
