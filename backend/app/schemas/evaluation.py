import uuid
from typing import Any

from pydantic import BaseModel


class EvaluationRequest(BaseModel):
    model_id: uuid.UUID
    dataset_id: uuid.UUID
    iou_threshold: float = 0.5


class EvaluationMetrics(BaseModel):
    map50: float
    map50_95: float
    precision: float
    recall: float
    per_class: dict[str, Any] | None = None


class EvaluationResponse(BaseModel):
    task_id: uuid.UUID
    model_id: uuid.UUID
    dataset_id: uuid.UUID
    status: str
    metrics: EvaluationMetrics | None = None
