"""task.priority and task.description

Revision ID: 0002_priority_description
Revises: 0001_initial
Create Date: 2026-05-13

## Трассируемость
Feature: F016 (priority), карточка задачи
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0002_priority_description"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column(
            "priority",
            sa.String(length=8),
            nullable=False,
            server_default="medium",
        ),
    )
    op.add_column(
        "tasks",
        sa.Column("description", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tasks", "description")
    op.drop_column("tasks", "priority")
