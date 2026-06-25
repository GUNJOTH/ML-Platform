import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model import MLModel
from app.repositories.base import BaseRepository


class MLModelRepository(BaseRepository[MLModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, MLModel)

    async def list_filtered(
        self,
        offset: int = 0,
        limit: int = 20,
        source: str | None = None,
        dataset_id: uuid.UUID | None = None,
    ) -> list[MLModel]:
        stmt = select(MLModel)
        if source:
            stmt = stmt.where(MLModel.model_source == source)
        if dataset_id:
            stmt = stmt.where(MLModel.dataset_id == dataset_id)
        stmt = stmt.offset(offset).limit(limit).order_by(MLModel.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_dataset(self, dataset_id: uuid.UUID) -> list[MLModel]:
        stmt = (
            select(MLModel)
            .where(MLModel.dataset_id == dataset_id)
            .order_by(MLModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
