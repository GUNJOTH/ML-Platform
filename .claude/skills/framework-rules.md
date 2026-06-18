---
name: framework-rules
description: ML 框架适配器约定，扩展新框架时必读
alwaysApply: true
globs: "backend/app/frameworks/**/*.py"
---

# 框架适配规则

## 注册机制

- 每个 framework 子包（如 `frameworks/yolov8/`）必须在自己的 `__init__.py` 末尾调用：
  ```python
  from app.frameworks.registry import register_framework
  register_framework("ultralytics", YOLOv8Trainer, YOLOv8Evaluator, YOLOv8Predictor)
  ```
- `app/frameworks/__init__.py` 导入所有子包以触发注册
- 框架名称（如 `"ultralytics"`）必须与 `MLModel.framework` 字段一致

## BaseTrainer.train(config) 约定

`config: dict[str, Any]` 必须包含的字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `data_yaml_path` | str | 数据集 yaml 的绝对路径 |
| `model_version` | str | 框架内的模型版本（如 `"yolov8n"`） |
| `progress_file` | str | worker 写进度的文件路径 |
| `project_dir` | str | 训练产物根目录（如 `storage/runs/{task_id}`） |
| `run_name` | str | 训练子目录名（如 `"train"`） |

可选字段（每个框架自定义默认值）：`epochs` / `batch_size` / `img_size` / `device` / `pretrained` / `optimizer` / `lr0` 等。

返回值：

```python
{
    "weight_path": str,            # 必填，最终权重文件绝对路径
    "metrics": dict[str, float],   # 必填，至少含 map50 / precision / recall（检测任务）
}
```

## BasePredictor.predict(model_path, input_path) 约定

返回 `list[dict[str, Any]]`，每个元素：

```python
{
    "label": str,
    "confidence": float,
    "bbox": {"x": float, "y": float, "width": float, "height": float},  # 像素值
}
```

失败时抛 `app.exceptions.InferenceError`。

## BaseEvaluator.evaluate(config) 约定

`config` 必须包含 `model_path` / `data_yaml_path`，返回与 trainer 一致的 `metrics` 字典。

## 扩展新框架

按以下顺序：

1. 在 `frameworks/{name}/` 下新建 `trainer.py` / `predictor.py` / `evaluator.py`，分别继承 `BaseTrainer` / `BasePredictor` / `BaseEvaluator`
2. 写 `frameworks/{name}/__init__.py` 调用 `register_framework`
3. 在 `frameworks/__init__.py` 中 `import app.frameworks.{name}`
4. 不需要改 Service 层，Service 通过 `get_trainer(framework_name)` 获取实例

## 禁止事项

- 禁止在 framework 适配器中 import Service / Repository / Model 层
- 禁止 framework 适配器读写数据库
- 禁止跨 framework 互相 import（`yolov8/` 不能 import `frameworks/detr/`）
