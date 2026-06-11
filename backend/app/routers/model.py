import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.schemas.model import MLModelCreate, MLModelResponse, MLModelUpdate
from app.services.model import MLModelService

router = APIRouter(prefix="/models", tags=["models"])


def get_service(db: AsyncSession = Depends(get_db)) -> MLModelService:
    return MLModelService(db)


@router.get("", response_model=list[MLModelResponse])
async def list_models(
    page: int = 1, page_size: int = 20, service: MLModelService = Depends(get_service)
):
    offset = (page - 1) * page_size
    return await service.list_models(offset=offset, limit=page_size)


@router.post("", response_model=MLModelResponse, status_code=201)
async def create_model(data: MLModelCreate, service: MLModelService = Depends(get_service)):
    return await service.create_model(data)


@router.get("/{model_id}", response_model=MLModelResponse)
async def get_model(model_id: uuid.UUID, service: MLModelService = Depends(get_service)):
    entity = await service.get_model(model_id)
    if not entity:
        from app.exceptions import NotFoundError

        raise NotFoundError("Model not found")
    return entity


@router.put("/{model_id}", response_model=MLModelResponse)
async def update_model(
    model_id: uuid.UUID, data: MLModelUpdate, service: MLModelService = Depends(get_service)
):
    entity = await service.update_model(model_id, data)
    if not entity:
        from app.exceptions import NotFoundError

        raise NotFoundError("Model not found")
    return entity


@router.delete("/{model_id}", status_code=204)
async def delete_model(model_id: uuid.UUID, service: MLModelService = Depends(get_service)):
    deleted = await service.delete_model(model_id)
    if not deleted:
        from app.exceptions import NotFoundError

        raise NotFoundError("Model not found")
