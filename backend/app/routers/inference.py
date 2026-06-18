import uuid
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.services.inference import InferenceService

router = APIRouter(prefix="/inference", tags=["inference"])


class InferenceRunRequest(BaseModel):
    model_id: uuid.UUID
    image_path: str


@router.post("/run")
async def run_inference(
    data: InferenceRunRequest, db: AsyncSession = Depends(get_db)
) -> list[dict[str, Any]]:
    service = InferenceService(db)
    return await service.run_inference(data.model_id, data.image_path)
