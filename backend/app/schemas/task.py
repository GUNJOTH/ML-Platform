import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class TaskCreate(BaseModel):
    name: str
    task_type: str
    model_id: uuid.UUID | None = None
    dataset_id: uuid.UUID | None = None
    config: dict[str, Any] | None = None


class TaskResponse(BaseModel):
    id: uuid.UUID
    name: str
    task_type: str
    status: str
    model_id: uuid.UUID | None
    dataset_id: uuid.UUID | None
    config: dict[str, Any] | None
    progress: int
    result: dict[str, Any] | None
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
