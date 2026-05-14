"""tasks.source_chat_username + pending_tasks.source_chat_username

Revision ID: 0006_chat_username
Revises: 0005_people
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0006_chat_username"
down_revision: Union[str, None] = "0005_people"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("source_chat_username", sa.String(length=64), nullable=True))
    op.add_column("pending_tasks", sa.Column("source_chat_username", sa.String(length=80), nullable=True))


def downgrade() -> None:
    op.drop_column("pending_tasks", "source_chat_username")
    op.drop_column("tasks", "source_chat_username")
