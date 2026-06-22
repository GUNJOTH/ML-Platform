import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.exceptions import NotFoundError
from app.schemas.label import LabelCreate, LabelResponse, LabelUpdate
from app.services.label import LabelService

router = APIRouter(tags=["标签管理"])


def get_service(db: AsyncSession = Depends(get_db)) -> LabelService:
    return LabelService(db)


@router.get("/datasets/{dataset_id}/labels", response_model=list[LabelResponse], summary="查询数据集标签列表")
async def list_labels(dataset_id: uuid.UUID, service: LabelService = Depends(get_service)):
    return await service.list_by_dataset(dataset_id)


@router.post("/datasets/{dataset_id}/labels", response_model=LabelResponse, status_code=201, summary="创建标签")
async def create_label(
    dataset_id: uuid.UUID, data: LabelCreate, service: LabelService = Depends(get_service)
):
    return await service.create_label(dataset_id, data)


@router.put("/labels/{label_id}", response_model=LabelResponse, summary="更新标签")
async def update_label(
    label_id: uuid.UUID, data: LabelUpdate, service: LabelService = Depends(get_service)
):
    entity = await service.update_label(label_id, data)
    if not entity:
        raise NotFoundError("Label not found")
    return entity


@router.delete("/labels/{label_id}", status_code=204, summary="删除标签")
async def delete_label(label_id: uuid.UUID, service: LabelService = Depends(get_service)):
    deleted = await service.delete_label(label_id)
    if not deleted:
        raise NotFoundError("Label not found")
