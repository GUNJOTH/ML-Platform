import uuid

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.exceptions import NotFoundError
from app.schemas.model import MLModelCreate, MLModelResponse, MLModelUpdate
from app.services.model import MLModelService

router = APIRouter(prefix="/models", tags=["models"])


def get_service(db: AsyncSession = Depends(get_db)) -> MLModelService:
    return MLModelService(db)


@router.get("", response_model=list[MLModelResponse])
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


@router.post("", response_model=MLModelResponse, status_code=201)
async def create_model(
    data: MLModelCreate, service: MLModelService = Depends(get_service)
):
    return await service.create_model(data)


@router.post("/import", response_model=MLModelResponse, status_code=201)
async def import_model(
    name: str = Form(...),
    version: str | None = Form(None),
    framework: str = Form("ultralytics"),
    file: UploadFile = File(...),
    service: MLModelService = Depends(get_service),
):
    content = await file.read()
    return await service.import_model(name, version, framework, file.filename, content)


@router.get("/{model_id}", response_model=MLModelResponse)
async def get_model(
    model_id: uuid.UUID, service: MLModelService = Depends(get_service)
):
    entity = await service.get_model(model_id)
    if not entity:
        raise NotFoundError("Model not found")
    return entity


@router.put("/{model_id}", response_model=MLModelResponse)
async def update_model(
    model_id: uuid.UUID,
    data: MLModelUpdate,
    service: MLModelService = Depends(get_service),
):
    entity = await service.update_model(model_id, data)
    if not entity:
        raise NotFoundError("Model not found")
    return entity


@router.delete("/{model_id}", status_code=204)
async def delete_model(
    model_id: uuid.UUID, service: MLModelService = Depends(get_service)
):
    deleted = await service.delete_model(model_id)
    if not deleted:
        raise NotFoundError("Model not found")


@router.get("/{model_id}/download")
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
