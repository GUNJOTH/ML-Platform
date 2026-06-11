import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset import Dataset, Image
from app.repositories.base import BaseRepository


class DatasetRepository(BaseRepository[Dataset]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Dataset)

    async def get_by_name(self, name: str) -> Dataset | None:
        stmt = select(Dataset).where(Dataset.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class ImageRepository(BaseRepository[Image]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Image)

    async def list_by_dataset(
        self, dataset_id: uuid.UUID, offset: int = 0, limit: int = 50
    ) -> list[Image]:
        stmt = (
            select(Image)
            .where(Image.dataset_id == dataset_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
