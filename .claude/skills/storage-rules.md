---
name: storage-rules
description: storage 目录与文件生命周期规则，所有读写必须遵守
alwaysApply: true
globs: "backend/**/*.py"
---

# 存储规则

## 目录结构

```text
storage/
├─ datasets/{dataset_id}/
├─ exports/{export_id}/
├─ tasks/{task_id}/
├─ runs/{task_id}/
├─ models/{model_id}/
└─ uploads/
   ├─ datasets/
   ├─ models/
   └─ images/
```

## 路径生成

- 所有 `storage/` 路径统一通过 `app/core/storage/paths.py` 中的 `StoragePaths` 生成
- 禁止在业务代码里手写 `settings.storage_path / "xxx"` 这种分散拼接
- 外部库必须接收真实文件路径时，先通过 helper 解析，再传给外部库

## StorageBackend 使用

- 主进程中的业务文件读写优先通过 `StorageBackend`
- worker 进程允许直接用 `Path` 同步写任务状态文件
- 删除文件/目录时优先走 `StorageBackend.delete()` / `delete_dir()`

## 文件生命周期

- `tasks/` 和 `runs/` 随任务生命周期存在；删除任务时应一并删除
- 上传后仍需复用的文件可以保留
- 上传后只为一次处理服务的临时文件，处理完成后必须清理
- 推理上传图片属于一次性临时文件，推理完成后应删除

## 禁止事项

- 禁止在主进程 Service 中随意直接 `Path.write_text()` / `Path.write_bytes()`
- 禁止留下没有数据库记录、也没有业务入口的孤儿运行目录
- 禁止把运行期文件长期混放在源码目录
