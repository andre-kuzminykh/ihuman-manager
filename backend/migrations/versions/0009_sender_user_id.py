"""tasks/pending_tasks: source_sender_user_id

Revision ID: 0009_sender_user_id
Revises: 0008_msgctx_names
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0009_sender_user_id"
down_revision: Union[str, None] = "0008_msgctx_names"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("source_sender_user_id", sa.BigInteger(), nullable=True))
    op.add_column("pending_tasks", sa.Column("source_sender_user_id", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("pending_tasks", "source_sender_user_id")
    op.drop_column("tasks", "source_sender_user_id")
