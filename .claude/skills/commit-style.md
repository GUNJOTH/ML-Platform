---
name: commit-style
description: Git 提交规范
alwaysApply: true
---

# 提交规范

## 原则

- 一次提交只做一类紧密相关的修改
- 标题优先使用中文，简洁明确
- 正文说明“改了什么、为什么改、是否有风险”
- 不提交运行期文件、打包产物、日志、`.env`

## 推荐格式

标题：

```text
类型(范围)：简要说明
```

常用类型：

- `feat`
- `fix`
- `refactor`
- `docs`
- `style`
- `test`
- `chore`

常用范围：

- `backend`
- `frontend`
- `task`
- `inference`
- `training`
- `deploy`
- `docs`

## 中文示例

```text
fix(task)：修正运行中任务详情只显示训练日志
fix(inference)：推理完成后自动清理临时上传图片
chore(deploy)：补充项目一键打包脚本
```

## 额外要求

- 如果本次改动偏“减复杂度”，正文里写清删掉了什么复杂度
- 如果修改了部署配置，正文里写清重建命令和影响范围
- 如果某个函数/组件超出长度建议，正文里说明原因
