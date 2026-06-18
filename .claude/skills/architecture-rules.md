---
name: architecture-rules
description: 架构分层约束，确保代码可扩展性
alwaysApply: true
globs: "backend/**/*.py"
---

# 架构规则

## 分层约束（严格单向依赖）

```
Router → Service → Repository → Model
                ↘  Core (Storage / Runner / Framework Registry)
```

- Router 不写业务判断和数据库调用；纯参数转发可以写到 15 行
- Service 禁止直接 `import` SQLAlchemy 查询 API（`select`/`insert`/`update`/`delete`）
- Service 禁止直接调用 `session.add()` / `session.execute()`，必须通过 Repository
- Repository 不做跨表的业务规则判断；查询条件构造（`if filter: stmt = stmt.where(...)`）允许
- Model 层只定义表结构和关系，不含方法逻辑

## Service 间协作

- 禁止 Service 在 `__init__` 里 `new` 另一个 Service
- 禁止 Service 调用其他 Service 的 Repository
- 共享逻辑提到 `app/core/` 或独立 helper service，由 Router 层组合多个 Service
- Service 可以依赖 `app/core/` 下的抽象（StorageBackend、TaskRunner、framework registry）

## 扩展规则

- 新增功能先在 `core/` 定义抽象接口（Protocol 或 ABC），再写具体实现
- 新增数据库字段必须通过 Alembic 迁移，禁止手动改表
- 新增模块按 model → schema → repository → service → router 顺序创建
- `frameworks/` 新增框架适配时只实现 `base.py` 中定义的接口
- 每个 framework 子包必须在自己的 `__init__.py` 末尾调用 `register_framework()`，由 `app/frameworks/__init__.py` 触发导入

## 跨进程边界

- `app/runners/` 下的 worker 是独立进程，禁止 `import` Service 层
- worker 只通过 `storage/tasks/{id}/config.json` 接收输入
- worker 通过 `progress.json` / `result.json` 回传状态，不直接写数据库

## 禁止事项

- 禁止循环依赖
- 禁止硬编码配置值，所有配置走 `app/config.py`
- 禁止在业务代码中直接操作 `storage/` 下的文件，必须通过 `StorageBackend`
- 禁止 Router 内多次重复 `from app.exceptions import ...`，统一在文件顶部 import
