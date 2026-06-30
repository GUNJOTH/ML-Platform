---
name: deployment-rules
description: Docker、打包、部署与运维配置规则
alwaysApply: true
globs: "docker-compose.yml,**/Dockerfile,**/*.conf,**/*.ps1,README.md,.gitignore,.dockerignore"
---

# 部署与打包规则

## Docker Compose

- 非必要不增加周期性健康检查
- 如果删除 `healthcheck`，必须同步检查 `depends_on` 是否仍然成立
- GPU 相关配置只放在部署层，不侵入业务代码
- 端口、卷挂载、环境变量改动必须尽量局部，避免连带改业务逻辑

## 打包脚本

- 打包脚本必须可重复执行
- 默认排除 `.git`、`storage/`、缓存目录、打包产物、日志和大模型训练源码副本
- 新生成的部署压缩包必须被 `.gitignore` 忽略
- 打包脚本应输出最小必要的部署步骤

## 上传与代理

- Nginx 上传大小限制必须与实际数据集/模型上传场景匹配
- 代理 `/api` 和 WebSocket 时优先保持简单可读，不提前做复杂网关策略

## 文档

- README 中的部署命令必须与当前 `docker-compose.yml` 一致
- 如果新增打包脚本或部署前置步骤，README 必须同步更新

## 本项目额外要求

- 部署配置优先服务当前单机部署场景
- 不为了“未来集群化”提前引入复杂编排
- 能通过一条命令重建的，不拆成多套重复流程
