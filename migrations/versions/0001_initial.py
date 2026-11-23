"""Create professionals and appointments

Revision ID: 0001_initial
Revises:
Create Date: 2026-11-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "professionals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("specialty", sa.String(80), nullable=False),
    )
    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("professional_id", sa.Integer(), sa.ForeignKey("professionals.id"), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
    )
    op.create_index("appointments_professional_id_starts_at_idx", "appointments", ["professional_id", "starts_at"])


def downgrade() -> None:
    op.drop_index("appointments_professional_id_starts_at_idx", table_name="appointments")
    op.drop_table("appointments")
    op.drop_table("professionals")
