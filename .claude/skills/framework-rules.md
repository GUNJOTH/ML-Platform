---
name: framework-rules
description: 模型框架适配规则，扩展新框架时必须遵守
alwaysApply: true
globs: "backend/app/frameworks/**/*.py"
---

# 框架适配规则

## 注册机制

- 每个 framework 子包必须在自己的 `__init__.py` 中调用 `register_framework()`
- `app/frameworks/__init__.py` 负责触发各子包导入
- 注册名必须与 `MLModel.framework` 字段保持一致

## Trainer 约定

`BaseTrainer.train(config)` 的输入至少要支持：

- `weight_path`
- `data_yaml_path`
- `progress_file`
- `project_dir`
- `run_name`

常见可选字段包括：

- `epochs`
- `batch_size`
- `img_size`
- `device`
- `optimizer`
- `lr0`
- `workers`
- `pretrained`

返回结果至少应包含：

- `weight_path`
- `map50`
- `precision`
- `recall`

如果框架能提供更多信息，优先补充：

- `best_epoch`
- `map50_95`
- `train_duration_seconds`
- `weight_size_mb`
- `model_parameters`

## Predictor 约定

`BasePredictor.predict(model_path, input_path)` 返回 `list[dict[str, Any]]`

本项目当前检测任务统一返回结构：

```python
{
    "bbox": [x1, y1, x2, y2],
    "confidence": float,
    "class_id": int,
    "class_name": str,
}
```

- 新框架接入时优先兼容这个结构
- 禁止每个 framework 返回不同字段名，增加前端适配成本

## Evaluator 约定

- `evaluate(config)` 至少支持 `model_path` 和 `data_yaml_path`
- 返回结果应尽量与训练结果字段保持一致，减少前后端分支逻辑

## 禁止事项

- framework 适配层禁止依赖 Service / Repository / Router
- framework 适配层禁止直接写数据库
- 不同 framework 之间禁止互相 import
