from __future__ import annotations

import html
import json
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from fence_inspection import InMemoryRepository, InspectionSystem

DEFAULT_FRAMES = [
    {"blur_score": 0.8, "anomalies": []},
    {"blur_score": 0.7, "anomalies": [{"label": "fence_damage", "confidence": 0.88, "bbox": [20, 20, 70, 70]}]},
    {"blur_score": 0.65, "anomalies": [{"label": "fence_damage", "confidence": 0.91, "bbox": [22, 22, 72, 72]}]},
    {"blur_score": 0.62, "anomalies": [{"label": "fence_damage", "confidence": 0.93, "bbox": [24, 22, 74, 74]}]},
]


def run_pipeline_from_payload(payload_text: str) -> dict:
    frames = json.loads(payload_text)
    if not isinstance(frames, list):
        raise ValueError("frames payload 必须是 JSON 数组")

    repo = InMemoryRepository()
    system = InspectionSystem(repository=repo)
    task = system.create_task("web-task-001", "drone-web", "demo-area", "cam-web", "web-user")
    alerts = system.run_offline(task.task_id, "web-input.json", frames)

    return {
        "task_id": task.task_id,
        "total_frames": len(repo.frames[task.task_id]),
        "total_detections": len(repo.detections[task.task_id]),
        "total_tracks": len(repo.tracks[task.task_id]),
        "alerts": [asdict(a) for a in alerts],
    }


def _render_result(result: dict) -> str:
    return f"""
    <div class=\"result\">
      <h3>运行结果</h3>
      <pre>{html.escape(json.dumps(result, ensure_ascii=False, indent=2, default=str))}</pre>
    </div>
    """


def render_page(payload_text: str, result: dict | None = None, error: str | None = None) -> str:
    result_block = _render_result(result) if result else ""
    error_block = f"<div class='error'>错误：{html.escape(error)}</div>" if error else ""
    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>围栏异常巡检系统 Web Demo</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; max-width: 980px; }}
    textarea {{ width: 100%; min-height: 280px; font-family: monospace; }}
    button {{ padding: 10px 16px; margin-top: 10px; cursor: pointer; }}
    .error {{ color: #b00020; margin: 12px 0; }}
    .result pre {{ background: #f6f8fa; padding: 12px; border-radius: 6px; overflow-x: auto; }}
  </style>
</head>
<body>
  <h1>无人机围栏异常巡检系统（Web Demo）</h1>
  <p>在下方输入/修改帧数据 JSON，点击运行即可看到检测与告警结果。</p>
  {error_block}
  <form method=\"post\" action=\"/run\">
    <label for=\"payload\">帧数据(JSON数组):</label>
    <textarea id=\"payload\" name=\"payload\">{html.escape(payload_text)}</textarea>
    <br/>
    <button type=\"submit\">运行系统</button>
  </form>
  {result_block}
</body>
</html>
"""


class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path != "/":
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return
        self._send_html(render_page(json.dumps(DEFAULT_FRAMES, ensure_ascii=False, indent=2)))

    def do_POST(self) -> None:
        if self.path != "/run":
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        payload = parse_qs(body).get("payload", ["[]"])[0]

        try:
            result = run_pipeline_from_payload(payload)
            page = render_page(payload, result=result)
        except Exception as exc:  # noqa: BLE001
            page = render_page(payload, error=str(exc))

        self._send_html(page)

    def _send_html(self, content: str) -> None:
        data = content.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    with ThreadingHTTPServer((host, port), WebHandler) as server:
        print(f"Web demo running at http://{host}:{port}")
        server.serve_forever()


if __name__ == "__main__":
    run_server()
