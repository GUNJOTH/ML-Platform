import uuid
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.exceptions import NotFoundError
from app.schemas.model import MLModelResponse
from app.schemas.task import TaskArtifactsResponse, TaskCreate, TaskResponse
from app.services.task import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    return TaskService(db)


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    page: int = 1,
    page_size: int = 20,
    task_type: str | None = None,
    service: TaskService = Depends(get_service),
):
    return await service.list_tasks(offset=(page - 1) * page_size, limit=page_size, task_type=task_type)


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(data: TaskCreate, service: TaskService = Depends(get_service)):
    return await service.create_task(data)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: uuid.UUID, service: TaskService = Depends(get_service)):
    entity = await service.get_task(task_id)
    if not entity:
        raise NotFoundError("Task not found")
    return entity


@router.post("/{task_id}/cancel", response_model=TaskResponse)
async def cancel_task(
    task_id: uuid.UUID, service: TaskService = Depends(get_service)
):
    entity = await service.cancel_task(task_id)
    if not entity:
        raise NotFoundError("Task not found")
    return entity


@router.post("/{task_id}/start", response_model=TaskResponse)
async def start_task(
    task_id: uuid.UUID, service: TaskService = Depends(get_service)
):
    entity = await service.start_task(task_id)
    if not entity:
        raise NotFoundError("Task not found")
    return entity


@router.get("/{task_id}/progress")
async def get_task_progress(
    task_id: uuid.UUID, service: TaskService = Depends(get_service)
) -> dict[str, Any]:
    return await service.get_progress(task_id)


@router.post("/{task_id}/sync", response_model=TaskResponse)
async def sync_task_result(
    task_id: uuid.UUID, service: TaskService = Depends(get_service)
):
    entity = await service.sync_result(task_id)
    if not entity:
        raise NotFoundError("Task not found")
    return entity


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: uuid.UUID, service: TaskService = Depends(get_service)
):
    deleted = await service.delete_task(task_id)
    if not deleted:
        raise NotFoundError("Task not found")


@router.get("/{task_id}/history")
async def get_task_history(
    task_id: uuid.UUID, service: TaskService = Depends(get_service)
) -> list[dict[str, Any]]:
    return await service.get_history(task_id)


@router.get("/{task_id}/artifacts", response_model=TaskArtifactsResponse)
async def list_task_artifacts(
    task_id: uuid.UUID, service: TaskService = Depends(get_service)
):
    items = await service.list_artifacts(task_id)
    return TaskArtifactsResponse(items=items)


@router.get("/{task_id}/artifacts/{filename}")
async def get_task_artifact(
    task_id: uuid.UUID, filename: str, service: TaskService = Depends(get_service)
):
    path = await service.get_artifact_path(task_id, filename)
    if not path:
        raise NotFoundError("Task artifact not found")
    return FileResponse(path=path, filename=filename)


@router.post("/{task_id}/export-model", response_model=MLModelResponse)
async def export_task_model(
    task_id: uuid.UUID, service: TaskService = Depends(get_service)
):
    model = await service.export_model(task_id)
    if not model:
        raise NotFoundError("Task not found or no weight to export")
    return model
