---
name: architecture-rules
description: 后端分层与扩展规则，保证平台长期可维护
alwaysApply: true
globs: "backend/**/*.py"
---

# 架构规则

## 分层

```text
Router -> Service -> Repository -> Model
                 -> Core (storage / runner / framework)
```

- Router 只做参数接收、返回值组织、异常透传
- Service 负责业务流程，不直接写 SQLAlchemy 查询语句
- Repository 负责数据库访问，不承担跨模块业务决策
- Model 只定义表结构与关系

## 扩展原则

- 新功能先判断是否能复用现有模块
- 只有出现第二个稳定实现需求时，才新增抽象层
- 不为了“未来可能支持”提前把简单流程过度抽象
- 对外部系统差异明显的能力，优先落到 `core/` 或 `frameworks/`

## 跨模块约束

- Service 不直接 new 其他 Service
- 禁止跨 Service 直接操作对方 Repository
- 共享逻辑优先提取到 helper / core，而不是层层互调

## 本项目额外要求

- 训练、评估、推理是三条独立业务链，禁止为了统一而强行耦合
- Docker、打包、部署属于运维配置，不应侵入训练/推理主流程
- 面向平台的“可维护性”优先于局部一次性技巧
