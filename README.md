# 无人机围栏异常巡检系统（原型代码）

这是一个按照你给出的分层架构实现的**可运行系统原型**，覆盖：

- 感知采集层：实时流适配、离线视频导入（模拟）
- 边缘智能分析层：视频调度、LSENet 去模糊（占位实现）、FAD-YOLOv11 检测（可替换实现）、DeepSORT 跟踪与一致性验证（轻量实现）
- 业务应用层：任务创建、运行控制、告警触发
- 数据管理层：任务、帧、检测、轨迹、告警统一存储（内存仓库）

## 目录结构

```text
src/fence_inspection/
├── models.py                # 领域模型（任务、帧、检测、轨迹、告警、配置）
├── storage.py               # 数据管理层（InMemoryRepository）
├── service.py               # 业务编排入口（InspectionSystem）
├── main.py                  # 演示入口
└── modules/
    ├── acquisition.py       # 感知采集层
    ├── scheduler.py         # 视频解析与调度
    ├── enhancement.py       # LSENet 增强模块（占位）
    ├── detection.py         # FAD-YOLOv11 检测模块（占位）
    └── tracking.py          # DeepSORT 跟踪 + 一致性验证（占位）
```

## 快速运行

```bash
python -m fence_inspection.main
```

运行后会生成 `run_result.json`，包含任务结果和告警信息。


## 网页运行（推荐）

```bash
PYTHONPATH=src python -m fence_inspection.webapp
```

浏览器打开：`http://127.0.0.1:8000`。

页面中可直接编辑 JSON 帧数据并点击“运行系统”，会返回检测、轨迹和告警结果。

## 测试

```bash
pytest -q
```

## 后续替换建议

1. 在 `modules/enhancement.py` 中接入真实 LSENet 推理。
2. 在 `modules/detection.py` 中接入真实 FAD-YOLOv11 模型。
3. 在 `modules/tracking.py` 中替换为 DeepSORT 正式实现并接入外观特征。
4. 在 `storage.py` 中替换为 PostgreSQL/ClickHouse + 对象存储。
5. 补充 Web UI 与实时视频叠加显示。
