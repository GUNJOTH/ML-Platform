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
```

- Router 层禁止直接调用 Repository
- Service 层禁止直接 import SQLAlchemy 内部 API（如 select, insert）
- Repository 层禁止包含业务逻辑判断
- Model 层只定义表结构和关系，不含方法逻辑

## 扩展规则

- 新增功能先在 core/ 定义抽象接口（Protocol 或 ABC），再写具体实现
- 新增数据库字段必须通过 Alembic 迁移，禁止手动改表
- 新增模块按 model → schema → repository → service → router 顺序创建
- frameworks/ 新增框架适配时，只实现 base.py 中定义的接口

## 禁止事项

- 禁止循环依赖
- 禁止 Service 之间互相调用对方的 Repository
- 禁止在 Router 层写超过 5 行的业务逻辑
- 禁止硬编码配置值，所有配置走 config.py
- 禁止在业务代码中直接操作文件系统，必须通过 StorageBackend
