import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.schemas.task import TaskResponse
from app.services.evaluation import EvaluationService
from app.services.task import TaskService

router = APIRouter(prefix="/evaluation", tags=["模型评估"])


class EvaluationRunRequest(BaseModel):
    model_id: uuid.UUID
    dataset_id: uuid.UUID


@router.post("/run", response_model=TaskResponse, status_code=202, summary="发起模型评估任务")
async def run_evaluation(
    data: EvaluationRunRequest, db: AsyncSession = Depends(get_db)
):
    eval_service = EvaluationService(db)
    task_service = TaskService(db)
    task_data = await eval_service.build_task(data.model_id, data.dataset_id)
    task = await task_service.create_task(task_data)
    return await task_service.start_task(task.id)
