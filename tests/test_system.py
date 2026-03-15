from fence_inspection import InMemoryRepository, InspectionSystem


def test_alert_generated_after_consistency_frames() -> None:
    repo = InMemoryRepository()
    system = InspectionSystem(repository=repo)
    system.create_task("t1", "d1", "a1", "dev1", "op")

    frames = [
        {"blur_score": 0.8, "anomalies": []},
        {"blur_score": 0.8, "anomalies": [{"label": "fence_damage", "confidence": 0.9, "bbox": (10, 10, 50, 50)}]},
        {"blur_score": 0.8, "anomalies": [{"label": "fence_damage", "confidence": 0.9, "bbox": (12, 10, 52, 50)}]},
        {"blur_score": 0.8, "anomalies": [{"label": "fence_damage", "confidence": 0.9, "bbox": (13, 10, 53, 50)}]},
    ]

    alerts = system.run_offline("t1", "demo.mp4", frames)

    assert len(alerts) >= 1
    assert alerts[0].label == "fence_damage"
    assert alerts[0].duration_frames >= 3


def test_confidence_filter_works() -> None:
    repo = InMemoryRepository()
    system = InspectionSystem(repository=repo)
    system.config.detection_confidence_threshold = 0.85
    system.create_task("t2", "d1", "a1", "dev1", "op")

    frames = [
        {"blur_score": 0.5, "anomalies": [{"label": "intrusion", "confidence": 0.7}]},
        {"blur_score": 0.5, "anomalies": [{"label": "intrusion", "confidence": 0.9}]},
    ]
    system.run_offline("t2", "demo2.mp4", frames)

    assert len(repo.detections["t2"]) == 1
    assert repo.detections["t2"][0].confidence == 0.9
