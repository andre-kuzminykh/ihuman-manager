"""
TaskFavoriteModel — звёздочка per-user.

## Трассируемость
Feature: F004
Scenarios: SC009, SC010

(user_id, task_id) — составной PK.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from model.base_model import Base, _utcnow


class TaskFavoriteModel(Base):
    __tablename__ = "task_favorites"

    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    task_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    __table_args__ = (PrimaryKeyConstraint("user_id", "task_id"),)
