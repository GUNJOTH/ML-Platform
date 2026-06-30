import uuid
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.exceptions import NotFoundError
from app.schemas.model import MLModelResponse
from app.schemas.task import (
    TaskArtifactsResponse,
    TaskCreate,
    TaskLogResponse,
    TaskResponse,
)
from app.services.task import TaskService

router = APIRouter(prefix="/tasks", tags=["任务管理"])


def get_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    return TaskService(db)


@router.get("", response_model=list[TaskResponse], summary="查询任务列表")
async def list_tasks(
    page: int = 1,
    page_size: int = 20,
    task_type: str | None = None,
    service: TaskService = Depends(get_service),
):
    return await service.list_tasks(
        offset=(page - 1) * page_size,
        limit=page_size,
        task_type=task_type,
    )


@router.post("", response_model=TaskResponse, status_code=201, summary="创建任务")
async def create_task(data: TaskCreate, service: TaskService = Depends(get_service)):
    return await service.create_task(data)


@router.get("/{task_id}", response_model=TaskResponse, summary="查询任务详情")
async def get_task(task_id: uuid.UUID, service: TaskService = Depends(get_service)):
    entity = await service.get_task(task_id)
    if not entity:
        raise NotFoundError("Task not found")
    return entity


@router.post("/{task_id}/cancel", response_model=TaskResponse, summary="取消任务")
async def cancel_task(
    task_id: uuid.UUID, service: TaskService = Depends(get_service)
):
    entity = await service.cancel_task(task_id)
    if not entity:
        raise NotFoundError("Task not found")
    return entity


@router.post("/{task_id}/start", response_model=TaskResponse, summary="启动任务")
async def start_task(
    task_id: uuid.UUID, service: TaskService = Depends(get_service)
):
    entity = await service.start_task(task_id)
    if not entity:
        raise NotFoundError("Task not found")
    return entity


@router.get("/{task_id}/progress", summary="查询任务进度")
async def get_task_progress(
    task_id: uuid.UUID, service: TaskService = Depends(get_service)
) -> dict[str, Any]:
    return await service.get_progress(task_id)


@router.post("/{task_id}/sync", response_model=TaskResponse, summary="同步任务结果")
async def sync_task_result(
    task_id: uuid.UUID, service: TaskService = Depends(get_service)
):
    entity = await service.sync_result(task_id)
    if not entity:
        raise NotFoundError("Task not found")
    return entity


@router.delete("/{task_id}", status_code=204, summary="删除任务")
async def delete_task(
    task_id: uuid.UUID, service: TaskService = Depends(get_service)
):
    deleted = await service.delete_task(task_id)
    if not deleted:
        raise NotFoundError("Task not found")


@router.get("/{task_id}/history", summary="查询任务历史指标")
async def get_task_history(
    task_id: uuid.UUID, service: TaskService = Depends(get_service)
) -> list[dict[str, Any]]:
    return await service.get_history(task_id)


@router.get("/{task_id}/logs/{stream}", response_model=TaskLogResponse, summary="查询任务日志")
async def get_task_log(
    task_id: uuid.UUID,
    stream: str,
    service: TaskService = Depends(get_service),
):
    content = await service.get_log_content(task_id, stream)
    return TaskLogResponse(stream=stream, content=content)


@router.get("/{task_id}/artifacts", response_model=TaskArtifactsResponse, summary="查询任务产物列表")
async def list_task_artifacts(
    task_id: uuid.UUID, service: TaskService = Depends(get_service)
):
    items = await service.list_artifacts(task_id)
    return TaskArtifactsResponse(items=items)


@router.get("/{task_id}/artifacts/{filename}", summary="获取单个任务产物文件")
async def get_task_artifact(
    task_id: uuid.UUID, filename: str, service: TaskService = Depends(get_service)
):
    path = await service.get_artifact_path(task_id, filename)
    if not path:
        raise NotFoundError("Task artifact not found")
    return FileResponse(path=path, filename=filename)


@router.post("/{task_id}/export-model", response_model=MLModelResponse, summary="导出训练产物为模型")
async def export_task_model(
    task_id: uuid.UUID, service: TaskService = Depends(get_service)
):
    model = await service.export_model(task_id)
    if not model:
        raise NotFoundError("Task not found or no weight to export")
    return model
