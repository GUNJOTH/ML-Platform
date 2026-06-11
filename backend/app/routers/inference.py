import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.schemas.inference import InferenceRequest, InferenceResponse
from app.services.inference import InferenceService

router = APIRouter(prefix="/inference", tags=["inference"])


@router.post("", response_model=InferenceResponse, status_code=202)
async def run_inference(
    data: InferenceRequest, db: AsyncSession = Depends(get_db)
):
    service = InferenceService(db)
    await service.run_inference(data.model_id, [], data.model_dump())
    return InferenceResponse(
        task_id=uuid.uuid4(),
        status="pending",
        results=None,
    )
