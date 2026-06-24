from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Task)

    async def list_by_status(self, status: str, offset: int = 0, limit: int = 20) -> list[Task]:
        stmt = select(Task).where(Task.status == status).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_type(self, task_type: str, offset: int = 0, limit: int = 20) -> list[Task]:
        stmt = (
            select(Task)
            .where(Task.task_type == task_type)
            .order_by(Task.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_dataset_export(self, dataset_export_id: str) -> list[Task]:
        stmt = select(Task).where(Task.dataset_export_id == dataset_export_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_dataset_version(self, dataset_version_id: str) -> list[Task]:
        stmt = select(Task).where(Task.dataset_version_id == dataset_version_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
