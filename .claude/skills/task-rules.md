---
name: task-rules
description: 任务系统约定（状态机、Runner 接口、worker 通信）
alwaysApply: true
globs: "backend/**/*.py"
---

# 任务规则

## TaskStatus 枚举（强制）

定义在 `app/models/task.py` 中：

```python
import enum

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

- 数据库字段使用 `SQLEnum(TaskStatus)` 而非 `String`
- 业务代码中**禁止**出现状态字符串字面量（`"pending"` / `"running"` 等），必须引用枚举
- Schema (Pydantic) 同步使用此枚举

## 状态机

```
PENDING → RUNNING → COMPLETED
                  ↘ FAILED
                  ↘ CANCELLED  (PENDING / RUNNING 均可 → CANCELLED)
```

- 终态 (`COMPLETED` / `FAILED` / `CANCELLED`) 不可再迁移
- `start_task` 仅当 `PENDING` 时执行
- `cancel_task` 当 `PENDING` 或 `RUNNING` 时执行

## TaskRunner 接口（强制）

`app/core/runner/base.py` 中：

```python
class TaskRunner(ABC):
    async def run(self, task_id: str, config: dict[str, Any]) -> dict[str, Any]: ...
    async def cancel(self, task_id: str) -> None: ...
    async def get_progress(self, task_id: str) -> int: ...
    async def get_result(self, task_id: str) -> dict[str, Any] | None: ...
```

- `run` 返回 `{"pid": int}`
- `get_progress` 返回 0-100，无 progress 文件时返回 0
- `get_result` 在 `result.json` 不存在时返回 `None`

## worker 通信契约

- 主进程通过 `StoragePaths.task_config(task_id)` 写 `config.json`
- worker 启动后第一件事：写 PID 到 `StoragePaths.task_pid(task_id)`
- worker 通过 `StoragePaths.task_progress(task_id)` 周期性写进度
- worker 完成时写 `result.json`，格式：

```python
# 成功
{"status": "completed", "weight_path": str, "metrics": dict[str, float], ...}

# 失败
{"status": "failed", "error": str, "traceback": str}
```

- worker 必须捕获顶层异常并写 `result.json`，禁止异常直接结束进程不留痕迹
- worker 进程的 stdout / stderr 重定向到 `StoragePaths.task_stdout/stderr`

## 进度推送

- WebSocket `/ws/tasks/{task_id}` 由 `routers/ws.py` 提供
- 推送频率：2 秒轮询 `progress.json` 一次
- 看到 `result.json` 后推送一条 `{"type": "complete", ...}` 然后关闭连接
