import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class InferenceRequest(BaseModel):
    model_id: uuid.UUID
    confidence: float = 0.25
    iou_threshold: float = 0.45


class InferenceResult(BaseModel):
    image_path: str
    detections: list[dict[str, Any]]
    inference_time_ms: float


class InferenceResponse(BaseModel):
    task_id: uuid.UUID
    status: str
    results: list[InferenceResult] | None = None
    created_at: datetime | None = None
