import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.annotation import Annotation
from app.models.dataset import Image
from app.repositories.base import BaseRepository


class AnnotationRepository(BaseRepository[Annotation]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Annotation)

    async def list_by_image(self, image_id: uuid.UUID) -> list[Annotation]:
        stmt = select(Annotation).where(Annotation.image_id == image_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_dataset(self, dataset_id: uuid.UUID) -> list[Annotation]:
        stmt = (
            select(Annotation)
            .join(Image, Annotation.image_id == Image.id)
            .where(Image.dataset_id == dataset_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_image(self, image_id: uuid.UUID) -> None:
        stmt = delete(Annotation).where(Annotation.image_id == image_id)
        await self.session.execute(stmt)
        await self.session.flush()
