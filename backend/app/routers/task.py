import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.schemas.task import TaskCreate, TaskResponse
from app.services.task import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    return TaskService(db)


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    page: int = 1, page_size: int = 20, service: TaskService = Depends(get_service)
):
    offset = (page - 1) * page_size
    return await service.list_tasks(offset=offset, limit=page_size)


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(data: TaskCreate, service: TaskService = Depends(get_service)):
    return await service.create_task(data)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: uuid.UUID, service: TaskService = Depends(get_service)):
    entity = await service.get_task(task_id)
    if not entity:
        from app.exceptions import NotFoundError

        raise NotFoundError("Task not found")
    return entity


@router.post("/{task_id}/cancel", response_model=TaskResponse)
async def cancel_task(task_id: uuid.UUID, service: TaskService = Depends(get_service)):
    entity = await service.cancel_task(task_id)
    if not entity:
        from app.exceptions import NotFoundError

        raise NotFoundError("Task not found")
    return entity
