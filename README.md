# AI Platform - 数据标注与模型训练平台

基于 FastAPI + Vue 3 的 AI 数据标注与模型训练管理平台。

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.11+ / FastAPI / SQLAlchemy 2.x / Alembic |
| 前端 | Vue 3 / Vite / TypeScript / Element Plus / Pinia |
| 数据库 | PostgreSQL |
| 依赖管理 | 后端 uv / 前端 pnpm |

## 项目结构

```text
backend/           后端 API 服务
frontend/          前端 SPA
storage/           运行期文件存储
.claude/skills/    项目规则与约束
```

## 快速启动

### 后端

```bash
cd backend
cp .env.example .env
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问：

- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- 健康检查: `http://localhost:8000/api/v1/health`

### 前端

```bash
cd frontend
pnpm install
pnpm dev
```

启动后访问：

- 前端开发地址：`http://localhost:5173`

## Docker 部署

项目提供了基于 `docker-compose.yml` 的单机部署方案，包含：

- `postgres`: 元数据数据库
- `backend`: FastAPI 后端服务
- `frontend`: Nginx 承载前端静态站点，并反向代理 `/api` 和 WebSocket

### 先打包代码再上传服务器

如果需要先打包项目代码再上传到服务器，可以在项目根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\package-deploy.ps1
```

执行后会在项目根目录生成形如 `ai-platform-deploy-YYYYMMDD.zip` 的部署包，并自动清理旧的同名前缀部署包。

### 服务器部署步骤

先把部署包上传到服务器，然后执行：

```bash
unzip ai-platform-deploy-YYYYMMDD.zip -d ai-platform
cd ai-platform
cp docker.env.example .env
docker compose --env-file .env up -d --build
```

说明：

- 需要先解压，再进入解压后的项目目录执行 `docker compose`
- `docker compose --build` 会直接读取当前目录下的 `docker-compose.yml`、`backend/`、`frontend/` 等源码文件，因此不能直接对 zip 文件执行
- 运行期文件会挂载到项目根目录 `storage/`
- 后端容器启动时会自动执行 `alembic upgrade head`
- 如需 GPU 训练，需要在宿主机安装 NVIDIA Container Toolkit，并保证 Docker 可访问 GPU

启动后访问：

- 前端：`http://localhost:18080`
- 后端： `http://localhost:18000`
- 后端健康检查：`http://localhost:18000/api/v1/health`

## 核心模块

| 模块 | 说明 |
|---|---|
| 数据集管理 | 上传、导入、标注入口、训练数据准备 |
| 标注工作台 | 图片标注、类别管理、导出标注结果 |
| 模型管理 | 模型注册、训练产物管理 |
| 训练任务 | 创建、监控、取消训练任务 |
| 模型评估 | 评估任务与结果展示 |
| 推理能力 | 图片推理与结果查看 |

## API 概览

```text
GET/POST    /api/v1/datasets
GET/POST    /api/v1/models
GET/POST    /api/v1/tasks

GET/POST    /api/v1/datasets/{id}/labels
GET         /api/v1/images/{id}/annotations
POST        /api/v1/annotations

POST        /api/v1/inference
POST        /api/v1/evaluation
```

## 架构原则

- 分层结构：Router -> Service -> Repository -> Model
- 存储抽象：默认本地存储，预留扩展空间
- 任务抽象：训练/评估任务通过统一任务模型管理
- 框架适配：`backend/app/frameworks/` 下按训练框架扩展

## 项目治理入口

- [治理约定](./GOVERNANCE.md)
- [贡献指南](./CONTRIBUTING.md)
- [安全策略](./SECURITY.md)
- Issue 与 Pull Request 请使用仓库模板，并记录实际验证证据。