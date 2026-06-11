import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AnnotationCreate(BaseModel):
    image_id: uuid.UUID
    label_id: uuid.UUID
    annotation_type: str = "bbox"
    data: dict[str, Any]


class AnnotationUpdate(BaseModel):
    label_id: uuid.UUID | None = None
    data: dict[str, Any] | None = None


class AnnotationResponse(BaseModel):
    id: uuid.UUID
    image_id: uuid.UUID
    label_id: uuid.UUID
    annotation_type: str
    data: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AnnotationBatchCreate(BaseModel):
    annotations: list[AnnotationCreate]
