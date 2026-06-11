import uuid
from datetime import datetime

from pydantic import BaseModel


class DatasetCreate(BaseModel):
    name: str
    description: str | None = None
    data_type: str = "image"


class DatasetUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None


class DatasetResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    data_type: str
    storage_path: str | None
    num_classes: int
    train_count: int
    val_count: int
    test_count: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ImageResponse(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID
    filename: str
    file_path: str
    width: int
    height: int
    split: str
    annotation_status: str
    created_at: datetime

    model_config = {"from_attributes": True}
