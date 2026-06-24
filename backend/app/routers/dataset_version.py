import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.exceptions import NotFoundError
from app.schemas.dataset_version import (
    DatasetExportCreate,
    DatasetExportResponse,
    DatasetVersionCreate,
    DatasetVersionResponse,
    DatasetVersionValidationResult,
)
from app.services.dataset_version import DatasetVersionService

router = APIRouter(prefix="/dataset-versions", tags=["数据集版本"])


def get_service(db: AsyncSession = Depends(get_db)) -> DatasetVersionService:
    return DatasetVersionService(db)


@router.get("", response_model=list[DatasetVersionResponse], summary="查询数据集版本列表")
async def list_dataset_versions(
    dataset_id: uuid.UUID | None = Query(None),
    page: int = 1,
    page_size: int = 50,
    service: DatasetVersionService = Depends(get_service),
):
    return await service.list_versions(
        dataset_id=dataset_id,
        offset=(page - 1) * page_size,
        limit=page_size,
    )


@router.post("", response_model=DatasetVersionResponse, status_code=201, summary="创建数据集版本")
async def create_dataset_version(
    data: DatasetVersionCreate,
    service: DatasetVersionService = Depends(get_service),
):
    return await service.create_version(data)


@router.post(
    "/validate-draft",
    response_model=DatasetVersionValidationResult,
    summary="创建前校验数据集版本",
)
async def validate_dataset_version_draft(
    data: DatasetVersionCreate,
    service: DatasetVersionService = Depends(get_service),
):
    return await service.validate_version_draft(data)


@router.get("/{version_id}", response_model=DatasetVersionResponse, summary="查询数据集版本详情")
async def get_dataset_version(
    version_id: uuid.UUID,
    service: DatasetVersionService = Depends(get_service),
):
    entity = await service.get_version(version_id)
    if not entity:
        raise NotFoundError("Dataset version not found")
    return entity


@router.post(
    "/{version_id}/validate",
    response_model=DatasetVersionValidationResult,
    summary="执行数据集版本校验",
)
async def validate_dataset_version(
    version_id: uuid.UUID,
    service: DatasetVersionService = Depends(get_service),
):
    return await service.validate_version(version_id)


@router.post(
    "/{version_id}/exports",
    response_model=DatasetExportResponse,
    status_code=201,
    summary="基于数据集版本创建导出记录",
)
async def create_dataset_export(
    version_id: uuid.UUID,
    data: DatasetExportCreate,
    service: DatasetVersionService = Depends(get_service),
):
    if data.dataset_version_id != version_id:
        raise NotFoundError("Dataset version payload mismatch")
    return await service.create_export(data)


@router.delete("/{version_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除数据集版本")
async def delete_dataset_version(
    version_id: uuid.UUID,
    service: DatasetVersionService = Depends(get_service),
):
    await service.delete_version(version_id)
