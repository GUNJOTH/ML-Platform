import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.annotation import Annotation
from app.repositories.annotation import AnnotationRepository
from app.schemas.annotation import AnnotationCreate, AnnotationUpdate


class AnnotationService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = AnnotationRepository(session)
        self.session = session

    async def list_by_image(self, image_id: uuid.UUID) -> list[Annotation]:
        return await self.repo.list_by_image(image_id)

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
