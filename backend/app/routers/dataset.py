import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.schemas.dataset import DatasetCreate, DatasetResponse, DatasetUpdate, ImageResponse
from app.services.dataset import DatasetService

router = APIRouter(prefix="/datasets", tags=["datasets"])


def get_service(db: AsyncSession = Depends(get_db)) -> DatasetService:
    return DatasetService(db)


@router.get("", response_model=list[DatasetResponse])
async def list_datasets(
    page: int = 1, page_size: int = 20, service: DatasetService = Depends(get_service)
):
    offset = (page - 1) * page_size
    return await service.list_datasets(offset=offset, limit=page_size)


@router.post("", response_model=DatasetResponse, status_code=201)
async def create_dataset(data: DatasetCreate, service: DatasetService = Depends(get_service)):
    return await service.create_dataset(data)


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(dataset_id: uuid.UUID, service: DatasetService = Depends(get_service)):
    entity = await service.get_dataset(dataset_id)
    if not entity:
        from app.exceptions import NotFoundError

        raise NotFoundError("Dataset not found")
    return entity


@router.put("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: uuid.UUID, data: DatasetUpdate, service: DatasetService = Depends(get_service)
):
    entity = await service.update_dataset(dataset_id, data)
    if not entity:
        from app.exceptions import NotFoundError

        raise NotFoundError("Dataset not found")
    return entity


@router.delete("/{dataset_id}", status_code=204)
async def delete_dataset(dataset_id: uuid.UUID, service: DatasetService = Depends(get_service)):
    deleted = await service.delete_dataset(dataset_id)
    if not deleted:
        from app.exceptions import NotFoundError

        raise NotFoundError("Dataset not found")


@router.get("/{dataset_id}/images", response_model=list[ImageResponse])
async def list_dataset_images(
    dataset_id: uuid.UUID,
    page: int = 1,
    page_size: int = 50,
    service: DatasetService = Depends(get_service),
):
    offset = (page - 1) * page_size
    return await service.get_images(dataset_id, offset=offset, limit=page_size)
