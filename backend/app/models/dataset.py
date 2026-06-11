from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Dataset(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "datasets"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    data_type: Mapped[str] = mapped_column(String(50), default="image")
    storage_path: Mapped[str | None] = mapped_column(String(500))
    num_classes: Mapped[int] = mapped_column(Integer, default=0)
    train_count: Mapped[int] = mapped_column(Integer, default=0)
    val_count: Mapped[int] = mapped_column(Integer, default=0)
    test_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="ready")

    labels: Mapped[list[Label]] = relationship(back_populates="dataset", cascade="all, delete")
    images: Mapped[list[Image]] = relationship(back_populates="dataset", cascade="all, delete")


class Label(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "labels"

    dataset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#FF0000")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    dataset: Mapped[Dataset] = relationship(back_populates="labels")


class Image(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "images"

    dataset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    width: Mapped[int] = mapped_column(Integer, default=0)
    height: Mapped[int] = mapped_column(Integer, default=0)
    split: Mapped[str] = mapped_column(String(10), default="train")
    annotation_status: Mapped[str] = mapped_column(String(20), default="unannotated")

    dataset: Mapped[Dataset] = relationship(back_populates="images")
    annotations: Mapped[list[Annotation]] = relationship(
        back_populates="image", cascade="all, delete"
    )
