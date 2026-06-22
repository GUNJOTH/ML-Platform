import uuid
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.storage.factory import get_storage
from app.exceptions import NotFoundError
from app.models.dataset import Dataset, Image, Label
from app.repositories.dataset import DatasetRepository, ImageRepository
from app.repositories.label import LabelRepository
from app.schemas.dataset import DatasetCreate, DatasetUpdate
from app.services.dataset_import import DatasetImporter


class DatasetService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = DatasetRepository(session)
        self.image_repo = ImageRepository(session)
        self.label_repo = LabelRepository(session)
        self.importer = DatasetImporter()
        self.storage = get_storage()

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

    async def update_dataset(
        self, dataset_id: uuid.UUID, data: DatasetUpdate
    ) -> Dataset | None:
        entity = await self.repo.get_by_id(dataset_id)
        if not entity:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(entity, field, value)
        return await self.repo.update(entity)

    async def delete_dataset(self, dataset_id: uuid.UUID) -> bool:
        entity = await self.repo.get_by_id(dataset_id)
        if not entity:
            return False
        await self.repo.delete(entity)
        relative_path = str(Path("datasets") / str(dataset_id))
        await self.storage.delete_dir(relative_path)
        return True

    async def get_images(
        self, dataset_id: uuid.UUID, offset: int = 0, limit: int = 50
    ) -> list[Image]:
        return await self.image_repo.list_by_dataset(
            dataset_id, offset=offset, limit=limit
        )

    async def get_image(self, image_id: uuid.UUID) -> Image | None:
        return await self.image_repo.get_by_id(image_id)

    async def get_image_file_path(self, image_id: uuid.UUID) -> str | None:
        image = await self.image_repo.get_by_id(image_id)
        if not image:
            return None
        p = Path(image.file_path)
        if not p.is_absolute():
            if p.parts and p.parts[0] == "storage":
                p = settings.storage_path.parent / p
            else:
                p = settings.storage_path / p
        return str(p) if p.exists() else None

    async def count_datasets(self) -> int:
        return await self.repo.count()

    async def upload_dataset_zip(self, dataset_id: uuid.UUID, content: bytes) -> dict[str, Any]:
        return await self.importer.upload_and_extract(str(dataset_id), content)

    async def detect_dataset_structure(self, dataset_id: uuid.UUID) -> dict[str, Any]:
        return self.importer.detect_structure(str(dataset_id))

    async def import_dataset(
        self, dataset_id: uuid.UUID, payload: dict[str, Any]
    ) -> Dataset:
        dataset = await self.repo.get_by_id(dataset_id)
        if not dataset:
            raise NotFoundError("Dataset not found")

        classes: list[str] = payload.get("classes", [])
        splits: dict[str, dict[str, Any]] = payload.get("splits", {})

        await self._create_labels(dataset_id, classes)
        await self._import_split_images(dataset_id, splits)

        dataset.num_classes = len(classes)
        dataset.train_count = splits.get("train", {}).get("count", 0)
        dataset.val_count = splits.get("valid", splits.get("val", {})).get("count", 0)
        dataset.test_count = splits.get("test", {}).get("count", 0)
        dataset.storage_path = self.importer.generate_data_yaml(str(dataset_id), classes)
        dataset.status = "ready"

        return await self.repo.update(dataset)

    async def _create_labels(self, dataset_id: uuid.UUID, classes: list[str]) -> None:
        for idx, name in enumerate(classes):
            await self.label_repo.create(
                Label(dataset_id=dataset_id, name=name, sort_order=idx)
            )

    async def _import_split_images(
        self, dataset_id: uuid.UUID, splits: dict[str, dict[str, Any]]
    ) -> None:
        for split_name in splits:
            normalized = "val" if split_name == "valid" else split_name
            for img in self.importer.list_images(str(dataset_id), split_name):
                await self.image_repo.create(
                    Image(
                        dataset_id=dataset_id,
                        filename=img["filename"],
                        file_path=img["path"],
                        split=normalized,
                    )
                )
