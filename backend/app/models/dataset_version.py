from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class DatasetVersion(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "dataset_versions"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    version_name: Mapped[str] = mapped_column(String(255), nullable=False)
    version_code: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="frozen")
    source_type: Mapped[str] = mapped_column(String(50), default="manual-freeze")
    export_format: Mapped[str] = mapped_column(String(20), default="yolo")
    include_splits: Mapped[list[str] | None] = mapped_column(JSON)
    split_strategy: Mapped[str | None] = mapped_column(String(50))
    split_config: Mapped[dict | None] = mapped_column(JSON)
    label_schema_snapshot: Mapped[list[dict] | None] = mapped_column(JSON)
    stats_snapshot: Mapped[dict | None] = mapped_column(JSON)
    validation_summary: Mapped[dict | None] = mapped_column(JSON)
    frozen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class DatasetExport(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "dataset_exports"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    dataset_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dataset_versions.id", ondelete="CASCADE"), nullable=False
    )
    export_name: Mapped[str] = mapped_column(String(255), nullable=False)
    export_format: Mapped[str] = mapped_column(String(20), default="yolo")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    split_config: Mapped[dict | None] = mapped_column(JSON)
    output_path: Mapped[str | None] = mapped_column(String(500))
    data_yaml_path: Mapped[str | None] = mapped_column(String(500))
    manifest_path: Mapped[str | None] = mapped_column(String(500))
    validation_summary: Mapped[dict | None] = mapped_column(JSON)
    error_message: Mapped[str | None] = mapped_column(Text)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
