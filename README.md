# AI Platform — 数据标注与模型训练平台

基于 FastAPI + Vue 3 的 AI 数据标注与模型训练管理平台。

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.11+ / FastAPI / SQLAlchemy 2.x (async) / Alembic |
| 前端 | Vue 3 + Vite + TypeScript + Element Plus + Pinia |
| 数据库 | PostgreSQL + Apache Doris |
| 依赖管理 | 后端 uv / 前端 pnpm |

## 项目结构

```
├── backend/          后端 API 服务
├── frontend/         前端 SPA
├── storage/          文件存储（运行时生成）
└── .claude/skills/   代码规范约束
```

## 快速启动

### 后端

```bash
cd backend
cp .env.example .env        # 修改数据库配置
uv sync                     # 安装依赖
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问：
- Swagger 文档: http://localhost:8000/docs
- ReDoc 文档: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/api/v1/health

### 前端

```bash
cd frontend
pnpm install
pnpm dev
```

访问 http://localhost:5173

## 核心模块

| 模块 | 说明 |
|---|---|
| 数据集管理 | 上传、分割(train/val/test)、类别定义 |
| 数据标注 | 内置 BBox 标注编辑器，预留分割/分类 |
| 模型管理 | 注册、版本追踪、权重存储 |
| 训练任务 | 创建/监控/取消，超参配置 |
| 模型推理 | 图片上传推理（预留） |
| 模型评估 | mAP/精确率/召回率（预留） |

## API 概览

```
POST /api/v1/upload/dataset         数据集上传
POST /api/v1/upload/model-weight    模型权重上传

GET/POST    /api/v1/datasets        数据集 CRUD
GET/POST    /api/v1/models          模型 CRUD
GET/POST    /api/v1/tasks           训练任务管理

POST        /api/v1/inference       模型推理
POST        /api/v1/evaluation      模型评估

GET/POST    /api/v1/datasets/{id}/labels     类别管理
GET         /api/v1/images/{id}/annotations  标注数据
POST        /api/v1/annotations              创建标注
```

## 数据库

- **PostgreSQL**: 元数据（数据集、模型、任务、标注）
- **Apache Doris**: OLAP 分析（检测结果明细、训练指标时序）

配置在 `.env` 文件中，参考 `backend/.env.example`。

## 架构原则

- 四层分离: Router → Service → Repository → Model
- 存储抽象: StorageBackend 接口，本地优先，预留 S3
- 任务抽象: TaskRunner 接口，预留异步队列
- 框架适配: frameworks/ 目录，按模型框架扩展
