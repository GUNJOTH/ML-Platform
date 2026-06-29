import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.deps import get_db
from app.exceptions import NotFoundError
from app.schemas.model import MLModelCreate, MLModelResponse, MLModelUpdate
from app.services.model import MLModelService
from app.utils.security import sanitize_filename

router = APIRouter(prefix="/models", tags=["模型管理"])


def get_service(db: AsyncSession = Depends(get_db)) -> MLModelService:
    return MLModelService(db)


@router.get("", response_model=list[MLModelResponse], summary="查询模型列表")
async def list_models(
    page: int = 1,
    page_size: int = 20,
    source: str | None = Query(None),
    dataset_id: uuid.UUID | None = Query(None),
    service: MLModelService = Depends(get_service),
):
    return await service.list_models(
        offset=(page - 1) * page_size,
        limit=page_size,
        source=source,
        dataset_id=dataset_id,
    )


@router.post("", response_model=MLModelResponse, status_code=201, summary="创建模型记录")
async def create_model(
    data: MLModelCreate, service: MLModelService = Depends(get_service)
):
    return await service.create_model(data)


@router.post("/import", response_model=MLModelResponse, status_code=201, summary="导入模型权重")
async def import_model(
    name: str = Form(...),
    version: str | None = Form(None),
    framework: str = Form("ultralytics"),
    file: UploadFile = File(...),
    service: MLModelService = Depends(get_service),
):
    max_size = settings.max_upload_size_mb * 1024 * 1024
    if file.size is not None and file.size > max_size:
        raise HTTPException(status_code=413, detail="File too large")
    filename = sanitize_filename(file.filename or "model.pt", "model.pt")
    try:
        return await service.import_model(name, version, framework, filename, file.file)
    except ValueError as e:
        raise HTTPException(status_code=413, detail=str(e)) from e


@router.get("/{model_id}", response_model=MLModelResponse, summary="查询模型详情")
async def get_model(
    model_id: uuid.UUID, service: MLModelService = Depends(get_service)
):
    entity = await service.get_model(model_id)
    if not entity:
        raise NotFoundError("Model not found")
    return entity


@router.put("/{model_id}", response_model=MLModelResponse, summary="更新模型信息")
async def update_model(
    model_id: uuid.UUID,
    data: MLModelUpdate,
    service: MLModelService = Depends(get_service),
):
    entity = await service.update_model(model_id, data)
    if not entity:
        raise NotFoundError("Model not found")
    return entity


@router.delete("/{model_id}", status_code=204, summary="删除模型")
async def delete_model(
    model_id: uuid.UUID, service: MLModelService = Depends(get_service)
):
    deleted = await service.delete_model(model_id)
    if not deleted:
        raise NotFoundError("Model not found")


@router.get("/{model_id}/download", summary="下载模型权重文件")
async def download_model(
    model_id: uuid.UUID, service: MLModelService = Depends(get_service)
):
    weight_info = await service.get_weight_path(model_id)
    if not weight_info:
        raise NotFoundError("Model weight not found")
    return FileResponse(
        path=weight_info["path"],
        filename=weight_info["filename"],
        media_type="application/octet-stream",
    )
