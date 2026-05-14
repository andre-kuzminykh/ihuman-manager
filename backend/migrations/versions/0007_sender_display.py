"""tasks.source_sender_display + pending_tasks.source_sender_display

Revision ID: 0007_sender_display
Revises: 0006_chat_username
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0007_sender_display"
down_revision: Union[str, None] = "0006_chat_username"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tasks", sa.Column("source_sender_display", sa.String(length=200), nullable=True)
    )
    op.add_column(
        "pending_tasks",
        sa.Column("source_sender_display", sa.String(length=200), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("pending_tasks", "source_sender_display")
    op.drop_column("tasks", "source_sender_display")
