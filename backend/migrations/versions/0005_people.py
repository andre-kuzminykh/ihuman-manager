"""people table

Revision ID: 0005_people
Revises: 0004_task_sender_username
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0005_people"
down_revision: Union[str, None] = "0004_task_sender_username"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "people",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=True, index=True),
        sa.Column("username", sa.String(length=64), nullable=True, index=True),
        sa.Column("first_name", sa.String(length=200), nullable=True),
        sa.Column("last_name", sa.String(length=200), nullable=True),
        sa.Column("is_bot", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("language_code", sa.String(length=8), nullable=True),
        sa.Column("is_premium", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("message_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("telegram_user_id", name="uq_people_tg_user_id"),
    )


def downgrade() -> None:
    op.drop_table("people")
