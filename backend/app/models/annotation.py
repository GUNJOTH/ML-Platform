from __future__ import annotations

import uuid

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Annotation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "annotations"

    image_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("images.id", ondelete="CASCADE"))
    label_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("labels.id", ondelete="CASCADE"))
    annotation_type: Mapped[str] = mapped_column(String(20), default="bbox")
    data: Mapped[dict] = mapped_column(JSON, nullable=False)

    image: Mapped["Image"] = relationship(back_populates="annotations")  # noqa: F821
    label: Mapped["Label"] = relationship()  # noqa: F821
