import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Task(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "tasks"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    task_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    model_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("models.id"))
    dataset_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("datasets.id"))
    config: Mapped[dict | None] = mapped_column(JSON)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    result: Mapped[dict | None] = mapped_column(JSON)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
