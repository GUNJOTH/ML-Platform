from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.postgres import engine
from app.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="AI 数据标注与模型训练平台",
    description=(
        "面向数据标注、模型训练、评估与推理的一体化平台接口文档。\n\n"
        "当前版本重点覆盖：数据集管理、标注管理、模型管理、任务调度、模型评估、模型推理与文件上传。"
    ),
    version="0.1.0",
    summary="平台后端 API 文档",
    openapi_tags=[
        {"name": "数据集管理", "description": "数据集的创建、查询、更新、删除、图片访问与导入确认。"},
        {"name": "标注管理", "description": "图片标注的查询、新建、修改、删除与批量替换。"},
        {"name": "标签管理", "description": "数据集类别标签的维护。"},
        {"name": "模型管理", "description": "模型的注册、导入、查询、更新、删除与权重下载。"},
        {"name": "任务管理", "description": "训练/评估等任务的创建、启动、同步、取消、删除与产物访问。"},
        {"name": "模型评估", "description": "发起评估任务并返回对应任务记录。"},
        {"name": "模型推理", "description": "基于指定模型对输入图片执行推理。"},
        {"name": "文件上传", "description": "上传数据集压缩包、模型权重或推理图片。"},
        {"name": "统计分析", "description": "平台统计与训练指标占位接口。"},
        {"name": "实时通信", "description": "任务进度与结果的 WebSocket 推送接口。"},
    ],
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get(
    "/api/v1/health",
    tags=["系统"],
    summary="健康检查",
    description="用于确认后端服务是否正常运行，并返回当前应用名称与运行环境。",
)
async def health_check():
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}
