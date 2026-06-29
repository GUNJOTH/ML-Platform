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
        self,
        dataset_id: uuid.UUID,
        offset: int = 0,
        limit: int = 50,
        split: str | None = None,
    ) -> list[Image]:
        stmt = select(Image).where(Image.dataset_id == dataset_id)
        if split:
            stmt = stmt.where(Image.split == split)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_dataset_and_split(self, dataset_id: uuid.UUID, split: str) -> int:
        from sqlalchemy import func

        stmt = (
            select(func.count())
            .select_from(Image)
            .where(Image.dataset_id == dataset_id, Image.split == split)
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one() or 0)
