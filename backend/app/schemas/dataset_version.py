import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DatasetVersionCreate(BaseModel):
    dataset_id: uuid.UUID
    version_name: str
    description: str | None = None
    source_type: str = "manual-freeze"
    export_format: str = "yolo"
    include_splits: list[str] = Field(default_factory=lambda: ["train", "val", "test"])
    split_strategy: str = "reuse-existing"
    split_config: dict[str, Any] | None = None


class DatasetVersionValidationIssue(BaseModel):
    code: str
    message: str
    level: str


class DatasetVersionValidationResult(BaseModel):
    passed: bool
    errors: list[DatasetVersionValidationIssue]
    warnings: list[DatasetVersionValidationIssue]
    summary: dict[str, Any]


class DatasetVersionResponse(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID
    version_name: str
    version_code: str
    description: str | None
    status: str
    source_type: str
    export_format: str
    include_splits: list[str] | None
    split_strategy: str | None
    split_config: dict[str, Any] | None
    label_schema_snapshot: list[dict[str, Any]] | None
    stats_snapshot: dict[str, Any] | None
    validation_summary: dict[str, Any] | None
    frozen_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DatasetExportCreate(BaseModel):
    dataset_version_id: uuid.UUID
    export_name: str
    export_format: str = "yolo"
    splits: list[str] = Field(default_factory=lambda: ["train", "val", "test"])
    extras: list[str] = Field(
        default_factory=lambda: ["include_images", "include_labels", "include_manifest"]
    )
    notes: str | None = None


class DatasetExportResponse(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID
    dataset_version_id: uuid.UUID
    export_name: str
    export_format: str
    status: str
    split_config: dict[str, Any] | None
    output_path: str | None
    data_yaml_path: str | None
    manifest_path: str | None
    validation_summary: dict[str, Any] | None
    error_message: str | None
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
