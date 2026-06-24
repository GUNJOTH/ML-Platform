import uuid

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_version import DatasetExport, DatasetVersion
from app.repositories.base import BaseRepository


class DatasetVersionRepository(BaseRepository[DatasetVersion]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DatasetVersion)

    async def list_by_dataset(
        self, dataset_id: uuid.UUID, offset: int = 0, limit: int = 50
    ) -> list[DatasetVersion]:
        stmt = (
            select(DatasetVersion)
            .where(DatasetVersion.dataset_id == dataset_id)
            .order_by(desc(DatasetVersion.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class DatasetExportRepository(BaseRepository[DatasetExport]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DatasetExport)

    async def list_filtered(
        self,
        dataset_id: uuid.UUID | None = None,
        dataset_version_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[DatasetExport]:
        stmt = select(DatasetExport)
        if dataset_id:
            stmt = stmt.where(DatasetExport.dataset_id == dataset_id)
        if dataset_version_id:
            stmt = stmt.where(DatasetExport.dataset_version_id == dataset_version_id)
        stmt = stmt.order_by(desc(DatasetExport.created_at)).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
