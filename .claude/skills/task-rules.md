---
name: task-rules
description: 任务系统约定，包括状态机、runner 接口和结果同步
alwaysApply: true
globs: "backend/**/*.py"
---

# 任务规则

## TaskStatus

- 统一使用 `app.models.task.TaskStatus`
- 禁止在业务代码中散落状态字符串字面量
- 终态为：`completed` / `failed` / `cancelled`
- 终态任务不能再流转到其他状态

## 状态机

- `pending -> running -> completed`
- `pending -> running -> failed`
- `pending -> cancelled`
- `running -> cancelled`

## TaskRunner 接口

`app/core/runner/base.py` 中的接口应保持一致：

```python
class TaskRunner(ABC):
    async def run(self, task_id: str, config: dict[str, Any]) -> dict[str, Any]: ...
    async def cancel(self, task_id: str) -> None: ...
    async def get_progress(self, task_id: str) -> int: ...
    async def get_result(self, task_id: str) -> dict[str, Any] | None: ...
    async def is_running(self, task_id: str) -> bool: ...
```

- `run()` 返回值至少包含 `pid`
- `get_progress()` 返回 0-100
- `get_result()` 在结果不存在时返回 `None`
- `is_running()` 用于最小存活校验，不扩展成复杂监控系统

## Worker 通信

- 主进程通过 `StoragePaths.task_config(task_id)` 写 `config.json`
- worker 启动后第一时间写 `pid`
- worker 周期写 `progress.json`
- worker 完成或失败必须写 `result.json`
- worker 的 `stdout` / `stderr` 必须重定向到任务目录

## 结果同步

- 主进程优先读取 `result.json`
- 仅在必要时做最小结果恢复或最小失败兜底
- 禁止把任务同步逻辑扩展成难以维护的多阶段状态系统
- “进程已退出但无结果文件”这类兜底逻辑必须保持简单、可解释、可回退

## 前端可见性

- 训练运行中允许查看日志
- 运行中详情默认只展示对当前排障有价值的信息
- 日志查看能力不等于完整可观测平台，禁止顺手扩成复杂日志系统
