import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dataset_files import read_image_size, resolve_storage_path
from app.models.dataset import Image, Label
from app.models.annotation import Annotation
from app.repositories.dataset import ImageRepository
from app.repositories.label import LabelRepository
from app.repositories.annotation import AnnotationRepository
from app.schemas.annotation import AnnotationCreate, AnnotationUpdate


class AnnotationService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = AnnotationRepository(session)
        self.image_repo = ImageRepository(session)
        self.label_repo = LabelRepository(session)
        self.session = session

    async def list_by_image(self, image_id: uuid.UUID) -> list[Annotation]:
        annotations = await self.repo.list_by_image(image_id)
        if annotations:
            return annotations

        image = await self.image_repo.get_by_id(image_id)
        if not image:
            return []

        labels = await self.label_repo.list_by_dataset(image.dataset_id)
        return self._load_from_yolo_label(image, labels)

    async def create_annotation(self, data: AnnotationCreate) -> Annotation:
        entity = Annotation(
            image_id=data.image_id,
            label_id=data.label_id,
            annotation_type=data.annotation_type,
            data=data.data,
        )
        return await self.repo.create(entity)

    async def update_annotation(
        self, annotation_id: uuid.UUID, data: AnnotationUpdate
    ) -> Annotation | None:
        entity = await self.repo.get_by_id(annotation_id)
        if not entity:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(entity, field, value)
        return await self.repo.update(entity)

    async def delete_annotation(self, annotation_id: uuid.UUID) -> bool:
        entity = await self.repo.get_by_id(annotation_id)
        if not entity:
            return False
        await self.repo.delete(entity)
        return True

    async def batch_create(self, items: list[AnnotationCreate]) -> list[Annotation]:
        results = []
        for item in items:
            entity = await self.create_annotation(item)
            results.append(entity)
        return results

    async def replace_for_image(
        self, image_id: uuid.UUID, items: list[AnnotationCreate]
    ) -> list[Annotation]:
        """Delete all existing annotations for an image, then create new ones."""
        await self.repo.delete_by_image(image_id)
        results = []
        for item in items:
            entity = await self.create_annotation(item)
            results.append(entity)
        return results

    def _load_from_yolo_label(self, image: Image, labels: list[Label]) -> list[Annotation]:
        label_path = self._resolve_label_path(image)
        if not label_path.exists():
            return []

        label_lookup = {index: label for index, label in enumerate(labels)}
        rows = [
            line.strip()
            for line in label_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        annotations: list[Annotation] = []

        for row in rows:
            parts = row.split()
            if len(parts) != 5:
                continue
            try:
                class_index = int(float(parts[0]))
                x_center, y_center, width, height = [float(value) for value in parts[1:]]
            except ValueError:
                continue

            label = label_lookup.get(class_index)
            image_width, image_height = self._resolve_image_size(image)
            if not label or image_width <= 0 or image_height <= 0:
                continue

            abs_width = width * image_width
            abs_height = height * image_height
            abs_x = x_center * image_width - abs_width / 2
            abs_y = y_center * image_height - abs_height / 2

            annotations.append(
                Annotation(
                    id=uuid.uuid4(),
                    image_id=image.id,
                    label_id=label.id,
                    annotation_type="bbox",
                    data={
                        "x": round(abs_x, 2),
                        "y": round(abs_y, 2),
                        "width": round(abs_width, 2),
                        "height": round(abs_height, 2),
                    },
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
            )
            setattr(annotations[-1], "label_name", label.name)
            setattr(annotations[-1], "color", label.color)

        return annotations

    @classmethod
    def _resolve_label_path(cls, image: Image) -> Path:
        image_path = resolve_storage_path(image.file_path)
        dataset_root = image_path.parent.parent.parent
        return dataset_root / "labels" / image.split / f"{Path(image.filename).stem}.txt"

    @classmethod
    def _resolve_image_size(cls, image: Image) -> tuple[int, int]:
        if image.width > 0 and image.height > 0:
            return image.width, image.height

        image_path = resolve_storage_path(image.file_path)
        if not image_path.exists():
            return 0, 0

        return read_image_size(image_path)
