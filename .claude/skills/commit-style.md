---
name: commit-style
description: Git 提交规范
alwaysApply: true
---

# 提交规范

## Conventional Commits

格式：`<type>(<scope>): <description>`

### type

- feat: 新功能
- fix: 修复
- refactor: 重构（不改变功能）
- docs: 文档
- style: 格式调整（不改变逻辑）
- test: 测试
- chore: 构建/工具/依赖

### scope

- backend, frontend, db, config, ci

### 示例

```
feat(backend): add dataset CRUD endpoints
fix(frontend): correct sidebar menu highlight
refactor(backend): extract base repository
```

## 规则

- 描述用英文，简洁明了
- 一次提交只做一件事
- 不提交 .env 文件和 storage/ 下的数据文件
