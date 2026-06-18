---
name: storage-rules
description: 文件存储约定，所有 storage/ 下读写必须遵守
alwaysApply: true
globs: "backend/**/*.py"
---

# 存储规则

## 目录结构（强制）

```
storage/
├── datasets/{dataset_id}/
│   ├── images/{train|val|test}/{filename}
│   ├── labels/{train|val|test}/{filename}.txt   # YOLO txt 格式
│   └── data.yaml                                 # 平台标准化的 yaml
├── tasks/{task_id}/
│   ├── config.json    # 主进程写，worker 读
│   ├── progress.json  # worker 写，主进程读
│   ├── result.json    # worker 写最终结果或错误
│   ├── pid            # worker 写 PID
│   ├── stdout.log     # subprocess stdout 重定向
│   └── stderr.log     # subprocess stderr 重定向
├── runs/{task_id}/    # 训练框架（如 ultralytics）的运行产物根目录
├── models/{model_id}/ # 模型权重存储
└── uploads/           # 上传后的临时文件，处理完必须清理
```

## 路径生成（强制）

- 所有上述路径**必须**通过 `app/core/storage/paths.py` 中的 `StoragePaths` helper 生成
- 禁止在业务代码中字符串拼接 `storage_path / "datasets" / str(id)` 这种写法
- `StoragePaths` 提供方法：`dataset_root(id)` / `dataset_images_dir(id, split)` / `dataset_labels_dir(id, split)` / `dataset_yaml(id)` / `task_root(id)` / `task_config(id)` / `task_progress(id)` / `task_result(id)` / `task_pid(id)` / `task_stdout(id)` / `task_stderr(id)` / `run_root(id)` / `model_dir(id)` / `upload_path(filename)`

## StorageBackend 使用

- 主进程读写 `storage/` 下文件**必须**通过 `StorageBackend`（异步接口）
- 与外部库交互的临时路径（YOLO 的 `data.yaml` 给 ultralytics 当输入、runs/ 由 ultralytics 自己写）允许直用 `Path`
- 上传的 zip 临时文件进 `uploads/`，处理完**必须**调 `StorageBackend.delete()` 清理

## worker 进程例外

- `app/runners/` 下的 worker 是独立 Python 进程，没有 async event loop 上下文
- worker 内**允许**用 `Path.write_text` / `Path.read_text` / `json.dump` 同步操作 task 目录
- worker 仍然必须通过 `StoragePaths` 获取路径，禁止字面量路径拼接

## 禁止事项

- 禁止 `os.remove` / `os.mkdir` / `shutil.copy` 等同步文件操作出现在主进程业务代码中
- 禁止在 Service 层 `Path.write_bytes` / `Path.write_text`
- 禁止访问其他用户的 `storage/` 数据（多租户预留）
