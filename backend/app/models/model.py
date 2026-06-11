import uuid

from sqlalchemy import JSON, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class MLModel(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "models"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str | None] = mapped_column(String(50))
    framework: Mapped[str] = mapped_column(String(50), default="ultralytics")
    description: Mapped[str | None] = mapped_column(Text)
    weight_path: Mapped[str | None] = mapped_column(String(500))
    model_size_mb: Mapped[float | None] = mapped_column(Float)
    parameters: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="ready")
    dataset_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("datasets.id"))
    metrics: Mapped[dict | None] = mapped_column(JSON)
