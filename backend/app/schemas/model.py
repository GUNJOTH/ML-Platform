import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class MLModelCreate(BaseModel):
    name: str
    version: str | None = None
    framework: str = "ultralytics"
    description: str | None = None
    dataset_id: uuid.UUID | None = None


class MLModelUpdate(BaseModel):
    name: str | None = None
    version: str | None = None
    description: str | None = None
    status: str | None = None
    metrics: dict[str, Any] | None = None


class MLModelResponse(BaseModel):
    id: uuid.UUID
    name: str
    version: str | None
    framework: str
    description: str | None
    weight_path: str | None
    model_size_mb: float | None
    parameters: str | None
    status: str
    dataset_id: uuid.UUID | None
    metrics: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
