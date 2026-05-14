"""message_context: sender_first_name + sender_last_name

Revision ID: 0008_msgctx_names
Revises: 0007_sender_display
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0008_msgctx_names"
down_revision: Union[str, None] = "0007_sender_display"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "message_context",
        sa.Column("sender_first_name", sa.String(length=200), nullable=True),
    )
    op.add_column(
        "message_context",
        sa.Column("sender_last_name", sa.String(length=200), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("message_context", "sender_last_name")
    op.drop_column("message_context", "sender_first_name")
