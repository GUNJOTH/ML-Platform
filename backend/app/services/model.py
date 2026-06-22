import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage.factory import get_storage
from app.core.storage.paths import StoragePaths
from app.models.model import MLModel
from app.repositories.model import MLModelRepository
from app.schemas.model import MLModelCreate, MLModelUpdate
from app.services.upload import ALLOWED_MODEL_EXTS


class MLModelService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = MLModelRepository(session)
        self.session = session
        self.storage = get_storage()

    async def list_models(
        self,
        offset: int = 0,
        limit: int = 20,
        source: str | None = None,
        dataset_id: uuid.UUID | None = None,
    ) -> list[MLModel]:
        return await self.repo.list_filtered(
            offset=offset, limit=limit, source=source, dataset_id=dataset_id
        )

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

    async def import_model(
        self,
        name: str,
        version: str | None,
        framework: str,
        filename: str,
        content: bytes,
    ) -> MLModel:
        from app.config import settings

        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_MODEL_EXTS:
            raise ValueError(f"Unsupported model format: {ext}")
        max_size = settings.max_upload_size_mb * 1024 * 1024
        if len(content) > max_size:
            raise ValueError("File too large")

        entity = MLModel(
            name=name,
            version=version,
            framework=framework,
            model_source="pretrained",
            status="ready",
        )
        entity = await self.repo.create(entity)

        model_dir = StoragePaths.model_dir(entity.id)
        save_path = str(model_dir / filename)
        relative_path = str(Path("models") / str(entity.id) / filename)
        await self.storage.save(relative_path, content)

        entity.weight_path = save_path
        entity.model_size_mb = round(len(content) / (1024 * 1024), 2)
        return await self.repo.update(entity)

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
        relative_path = str(Path("models") / str(model_id))
        await self.storage.delete_dir(relative_path)
        return True

    async def get_weight_path(self, model_id: uuid.UUID) -> dict[str, str] | None:
        entity = await self.repo.get_by_id(model_id)
        if not entity or not entity.weight_path:
            return None
        weight = Path(entity.weight_path)
        if not weight.exists():
            return None
        return {"path": str(weight), "filename": weight.name}
