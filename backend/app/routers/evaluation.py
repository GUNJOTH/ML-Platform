import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.schemas.evaluation import EvaluationRequest, EvaluationResponse
from app.services.evaluation import EvaluationService

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.post("", response_model=EvaluationResponse, status_code=202)
async def run_evaluation(
    data: EvaluationRequest, db: AsyncSession = Depends(get_db)
):
    service = EvaluationService(db)
    await service.run_evaluation(data.model_id, data.dataset_id, data.model_dump())
    return EvaluationResponse(
        task_id=uuid.uuid4(),
        model_id=data.model_id,
        dataset_id=data.dataset_id,
        status="pending",
        metrics=None,
    )
