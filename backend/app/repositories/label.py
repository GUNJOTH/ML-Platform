import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset import Label
from app.repositories.base import BaseRepository


class LabelRepository(BaseRepository[Label]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Label)

    async def list_by_dataset(self, dataset_id: uuid.UUID) -> list[Label]:
        stmt = (
            select(Label)
            .where(Label.dataset_id == dataset_id)
            .order_by(Label.sort_order)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
