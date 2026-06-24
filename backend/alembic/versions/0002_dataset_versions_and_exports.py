"""dataset versions and exports

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, UUID

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_versions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("dataset_id", UUID(as_uuid=True), sa.ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_name", sa.String(255), nullable=False),
        sa.Column("version_code", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("status", sa.String(20), server_default="frozen"),
        sa.Column("source_type", sa.String(50), server_default="manual-freeze"),
        sa.Column("export_format", sa.String(20), server_default="yolo"),
        sa.Column("include_splits", JSON),
        sa.Column("split_strategy", sa.String(50)),
        sa.Column("split_config", JSON),
        sa.Column("label_schema_snapshot", JSON),
        sa.Column("stats_snapshot", JSON),
        sa.Column("validation_summary", JSON),
        sa.Column("frozen_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "dataset_exports",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("dataset_id", UUID(as_uuid=True), sa.ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dataset_version_id", UUID(as_uuid=True), sa.ForeignKey("dataset_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("export_name", sa.String(255), nullable=False),
        sa.Column("export_format", sa.String(20), server_default="yolo"),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("split_config", JSON),
        sa.Column("output_path", sa.String(500)),
        sa.Column("data_yaml_path", sa.String(500)),
        sa.Column("manifest_path", sa.String(500)),
        sa.Column("validation_summary", JSON),
        sa.Column("error_message", sa.Text()),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.add_column("tasks", sa.Column("dataset_version_id", UUID(as_uuid=True), nullable=True))
    op.add_column("tasks", sa.Column("dataset_export_id", UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(None, "tasks", "dataset_versions", ["dataset_version_id"], ["id"])
    op.create_foreign_key(None, "tasks", "dataset_exports", ["dataset_export_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint(None, "tasks", type_="foreignkey")
    op.drop_constraint(None, "tasks", type_="foreignkey")
    op.drop_column("tasks", "dataset_export_id")
    op.drop_column("tasks", "dataset_version_id")
    op.drop_table("dataset_exports")
    op.drop_table("dataset_versions")
