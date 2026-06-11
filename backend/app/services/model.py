import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model import MLModel
from app.repositories.model import MLModelRepository
from app.schemas.model import MLModelCreate, MLModelUpdate


class MLModelService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = MLModelRepository(session)
        self.session = session

    async def list_models(self, offset: int = 0, limit: int = 20) -> list[MLModel]:
        return await self.repo.list(offset=offset, limit=limit)

    async def get_model(self, model_id: uuid.UUID) -> MLModel | None:
        return await self.repo.get_by_id(model_id)

    async def create_model(self, data: MLModelCreate) -> MLModel:
        entity = MLModel(
            name=data.name,
            version=data.version,
            framework=data.framework,
            description=data.description,
            dataset_id=data.dataset_id,
        )
        return await self.repo.create(entity)

    async def update_model(self, model_id: uuid.UUID, data: MLModelUpdate) -> MLModel | None:
        entity = await self.repo.get_by_id(model_id)
        if not entity:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(entity, field, value)
        return await self.repo.update(entity)

    async def delete_model(self, model_id: uuid.UUID) -> bool:
        entity = await self.repo.get_by_id(model_id)
        if not entity:
            return False
        await self.repo.delete(entity)
        return True
