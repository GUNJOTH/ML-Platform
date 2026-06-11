import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset import Dataset
from app.repositories.dataset import DatasetRepository, ImageRepository
from app.schemas.dataset import DatasetCreate, DatasetUpdate


class DatasetService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = DatasetRepository(session)
        self.image_repo = ImageRepository(session)
        self.session = session

    async def list_datasets(self, offset: int = 0, limit: int = 20) -> list[Dataset]:
        return await self.repo.list(offset=offset, limit=limit)

    async def get_dataset(self, dataset_id: uuid.UUID) -> Dataset | None:
        return await self.repo.get_by_id(dataset_id)

    async def create_dataset(self, data: DatasetCreate) -> Dataset:
        entity = Dataset(
            name=data.name,
            description=data.description,
            data_type=data.data_type,
        )
        return await self.repo.create(entity)

    async def update_dataset(self, dataset_id: uuid.UUID, data: DatasetUpdate) -> Dataset | None:
        entity = await self.repo.get_by_id(dataset_id)
        if not entity:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(entity, field, value)
        return await self.repo.update(entity)

    async def delete_dataset(self, dataset_id: uuid.UUID) -> bool:
        entity = await self.repo.get_by_id(dataset_id)
        if not entity:
            return False
        await self.repo.delete(entity)
        return True

    async def get_images(self, dataset_id: uuid.UUID, offset: int = 0, limit: int = 50):
        return await self.image_repo.list_by_dataset(dataset_id, offset=offset, limit=limit)

    async def count_datasets(self) -> int:
        return await self.repo.count()
