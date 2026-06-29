import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.deps import get_db
from app.exceptions import NotFoundError
from app.schemas.dataset import (
    DatasetCreate,
    DatasetResponse,
    DatasetUpdate,
    ImageResponse,
)
from app.services.annotation_export import AnnotationExportService
from app.services.dataset import DatasetService

router = APIRouter(prefix="/datasets", tags=["数据集管理"])


def get_service(db: AsyncSession = Depends(get_db)) -> DatasetService:
    return DatasetService(db)


@router.get("", response_model=list[DatasetResponse], summary="查询数据集列表")
async def list_datasets(
    page: int = 1, page_size: int = 20, service: DatasetService = Depends(get_service)
):
    return await service.list_datasets(offset=(page - 1) * page_size, limit=page_size)


@router.post("", response_model=DatasetResponse, status_code=201, summary="创建数据集")
async def create_dataset(
    data: DatasetCreate, service: DatasetService = Depends(get_service)
):
    return await service.create_dataset(data)


@router.get("/{dataset_id}", response_model=DatasetResponse, summary="查询数据集详情")
async def get_dataset(
    dataset_id: uuid.UUID, service: DatasetService = Depends(get_service)
):
    entity = await service.get_dataset(dataset_id)
    if not entity:
        raise NotFoundError("Dataset not found")
    return entity


@router.put("/{dataset_id}", response_model=DatasetResponse, summary="更新数据集信息")
async def update_dataset(
    dataset_id: uuid.UUID,
    data: DatasetUpdate,
    service: DatasetService = Depends(get_service),
):
    entity = await service.update_dataset(dataset_id, data)
    if not entity:
        raise NotFoundError("Dataset not found")
    return entity


@router.delete("/{dataset_id}", status_code=204, summary="删除数据集")
async def delete_dataset(
    dataset_id: uuid.UUID, service: DatasetService = Depends(get_service)
):
    deleted = await service.delete_dataset(dataset_id)
    if not deleted:
        raise NotFoundError("Dataset not found")


@router.get("/{dataset_id}/images", response_model=list[ImageResponse], summary="查询数据集图片列表")
async def list_dataset_images(
    dataset_id: uuid.UUID,
    page: int = 1,
    page_size: int = 50,
    split: str | None = Query(None),
    service: DatasetService = Depends(get_service),
):
    return await service.get_images(
        dataset_id, offset=(page - 1) * page_size, limit=page_size, split=split
    )


@router.delete("/images/{image_id}", status_code=204, summary="删除数据集图片")
async def delete_dataset_image(
    image_id: uuid.UUID, service: DatasetService = Depends(get_service)
):
    deleted = await service.delete_image(image_id)
    if not deleted:
        raise NotFoundError("Image not found")


@router.post("/{dataset_id}/upload-zip", summary="上传数据集压缩包")
async def upload_dataset_zip(
    dataset_id: uuid.UUID,
    file: UploadFile = File(...),
    service: DatasetService = Depends(get_service),
) -> dict[str, Any]:
    max_size = settings.max_upload_size_mb * 1024 * 1024
    if file.size is not None and file.size > max_size:
        raise HTTPException(status_code=413, detail="File too large")
    try:
        return await service.upload_dataset_zip(dataset_id, file.file)
    except ValueError as e:
        raise HTTPException(status_code=413, detail=str(e)) from e


@router.get("/{dataset_id}/detect", summary="检测数据集目录结构")
async def detect_dataset_structure(
    dataset_id: uuid.UUID, service: DatasetService = Depends(get_service)
) -> dict[str, Any]:
    return await service.detect_dataset_structure(dataset_id)


@router.post("/{dataset_id}/confirm-import", response_model=DatasetResponse, summary="确认并导入数据集")
async def confirm_dataset_import(
    dataset_id: uuid.UUID,
    payload: dict[str, Any],
    service: DatasetService = Depends(get_service),
):
    return await service.import_dataset(dataset_id, payload)


@router.get("/images/{image_id}/file", summary="获取图片原始文件")
async def get_image_file(
    image_id: uuid.UUID, service: DatasetService = Depends(get_service)
):
    resolved = await service.get_image_file_path(image_id)
    if not resolved:
        raise NotFoundError("Image file not found")
    return FileResponse(path=resolved, media_type="image/jpeg")


@router.post("/{dataset_id}/export-annotated", response_model=DatasetResponse, summary="导出标注结果为新数据集")
async def export_annotated_dataset(
    dataset_id: uuid.UUID,
    payload: dict[str, Any],
    db: AsyncSession = Depends(get_db),
):
    export_service = AnnotationExportService(db)
    return await export_service.export_dataset(
        source_dataset_id=dataset_id,
        annotations=payload.get("annotations", {}),
        mode=payload.get("mode", "new"),
    )
