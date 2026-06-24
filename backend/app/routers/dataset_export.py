import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.exceptions import NotFoundError
from app.schemas.dataset_version import DatasetExportResponse
from app.services.dataset_version import DatasetVersionService

router = APIRouter(prefix="/dataset-exports", tags=["数据集导出"])


def get_service(db: AsyncSession = Depends(get_db)) -> DatasetVersionService:
    return DatasetVersionService(db)


@router.get("", response_model=list[DatasetExportResponse], summary="查询数据集导出记录列表")
async def list_dataset_exports(
    dataset_id: uuid.UUID | None = Query(None),
    dataset_version_id: uuid.UUID | None = Query(None),
    page: int = 1,
    page_size: int = 50,
    service: DatasetVersionService = Depends(get_service),
):
    return await service.list_exports(
        dataset_id=dataset_id,
        dataset_version_id=dataset_version_id,
        offset=(page - 1) * page_size,
        limit=page_size,
    )


@router.get("/{export_id}", response_model=DatasetExportResponse, summary="查询数据集导出记录详情")
async def get_dataset_export(
    export_id: uuid.UUID,
    service: DatasetVersionService = Depends(get_service),
):
    entity = await service.get_export(export_id)
    if not entity:
        raise NotFoundError("Dataset export not found")
    return entity


@router.delete("/{export_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除数据集导出记录")
async def delete_dataset_export(
    export_id: uuid.UUID,
    service: DatasetVersionService = Depends(get_service),
):
    await service.delete_export(export_id)
