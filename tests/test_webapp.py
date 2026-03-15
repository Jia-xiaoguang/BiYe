import json

from fence_inspection.webapp import render_page, run_pipeline_from_payload


def test_run_pipeline_from_payload_returns_alerts() -> None:
    payload = json.dumps(
        [
            {"blur_score": 0.8, "anomalies": []},
            {"blur_score": 0.8, "anomalies": [{"label": "fence_damage", "confidence": 0.9, "bbox": [10, 10, 50, 50]}]},
            {"blur_score": 0.8, "anomalies": [{"label": "fence_damage", "confidence": 0.9, "bbox": [12, 10, 52, 50]}]},
            {"blur_score": 0.8, "anomalies": [{"label": "fence_damage", "confidence": 0.9, "bbox": [14, 10, 54, 50]}]},
        ]
    )

    result = run_pipeline_from_payload(payload)

    assert result["task_id"] == "web-task-001"
    assert result["total_detections"] >= 3
    assert len(result["alerts"]) >= 1


def test_render_page_contains_title() -> None:
    page = render_page("[]")
    assert "围栏异常巡检系统（Web Demo）" in page
