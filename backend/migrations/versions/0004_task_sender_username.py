"""tasks.source_sender_username

Revision ID: 0004_task_sender_username
Revises: 0003_business_connections
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0004_task_sender_username"
down_revision: Union[str, None] = "0003_business_connections"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column("source_sender_username", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tasks", "source_sender_username")
