import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset import Label
from app.repositories.label import LabelRepository
from app.schemas.label import LabelCreate, LabelUpdate


class LabelService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = LabelRepository(session)
        self.session = session

    async def list_by_dataset(self, dataset_id: uuid.UUID) -> list[Label]:
        return await self.repo.list_by_dataset(dataset_id)

    async def create_label(self, dataset_id: uuid.UUID, data: LabelCreate) -> Label:
        entity = Label(
            dataset_id=dataset_id,
            name=data.name,
            color=data.color,
            sort_order=data.sort_order,
        )
        return await self.repo.create(entity)

    async def update_label(self, label_id: uuid.UUID, data: LabelUpdate) -> Label | None:
        entity = await self.repo.get_by_id(label_id)
        if not entity:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(entity, field, value)
        return await self.repo.update(entity)

    async def delete_label(self, label_id: uuid.UUID) -> bool:
        entity = await self.repo.get_by_id(label_id)
        if not entity:
            return False
        await self.repo.delete(entity)
        return True
