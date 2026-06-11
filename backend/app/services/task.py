import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = TaskRepository(session)
        self.session = session

    async def list_tasks(self, offset: int = 0, limit: int = 20) -> list[Task]:
        return await self.repo.list(offset=offset, limit=limit)

    async def get_task(self, task_id: uuid.UUID) -> Task | None:
        return await self.repo.get_by_id(task_id)

    async def create_task(self, data: TaskCreate) -> Task:
        entity = Task(
            name=data.name,
            task_type=data.task_type,
            model_id=data.model_id,
            dataset_id=data.dataset_id,
            config=data.config,
        )
        return await self.repo.create(entity)

    async def cancel_task(self, task_id: uuid.UUID) -> Task | None:
        entity = await self.repo.get_by_id(task_id)
        if not entity:
            return None
        if entity.status in ("pending", "running"):
            entity.status = "cancelled"
            return await self.repo.update(entity)
        return entity
