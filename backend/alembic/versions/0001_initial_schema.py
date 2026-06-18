"""initial schema

Revision ID: 0001
Revises: None
Create Date: 2026-06-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "datasets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), unique=True, nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("data_type", sa.String(50), server_default="image"),
        sa.Column("storage_path", sa.String(500)),
        sa.Column("num_classes", sa.Integer, server_default="0"),
        sa.Column("train_count", sa.Integer, server_default="0"),
        sa.Column("val_count", sa.Integer, server_default="0"),
        sa.Column("test_count", sa.Integer, server_default="0"),
        sa.Column("status", sa.String(20), server_default="ready"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "labels",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("dataset_id", UUID(as_uuid=True), sa.ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("color", sa.String(7), server_default="#FF0000"),
        sa.Column("sort_order", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "images",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("dataset_id", UUID(as_uuid=True), sa.ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("width", sa.Integer, server_default="0"),
        sa.Column("height", sa.Integer, server_default="0"),
        sa.Column("split", sa.String(10), server_default="train"),
        sa.Column("annotation_status", sa.String(20), server_default="unannotated"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "annotations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("image_id", UUID(as_uuid=True), sa.ForeignKey("images.id", ondelete="CASCADE"), nullable=False),
        sa.Column("label_id", UUID(as_uuid=True), sa.ForeignKey("labels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("annotation_type", sa.String(20), server_default="bbox"),
        sa.Column("data", JSON, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "models",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("version", sa.String(50)),
        sa.Column("framework", sa.String(50), server_default="ultralytics"),
        sa.Column("description", sa.Text),
        sa.Column("weight_path", sa.String(500)),
        sa.Column("model_size_mb", sa.Float),
        sa.Column("parameters", sa.String(50)),
        sa.Column("status", sa.String(20), server_default="ready"),
        sa.Column("model_source", sa.String(20), server_default="pretrained"),
        sa.Column("dataset_id", UUID(as_uuid=True), sa.ForeignKey("datasets.id")),
        sa.Column("metrics", JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "tasks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("task_type", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("model_id", UUID(as_uuid=True), sa.ForeignKey("models.id")),
        sa.Column("dataset_id", UUID(as_uuid=True), sa.ForeignKey("datasets.id")),
        sa.Column("config", JSON),
        sa.Column("progress", sa.Integer, server_default="0"),
        sa.Column("result", JSON),
        sa.Column("error_message", sa.Text),
        sa.Column("worker_pid", sa.Integer),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("tasks")
    op.drop_table("models")
    op.drop_table("annotations")
    op.drop_table("images")
    op.drop_table("labels")
    op.drop_table("datasets")
