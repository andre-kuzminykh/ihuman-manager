"""
NotificationLogModel — журнал отправленных уведомлений (защита от дублей).

## Трассируемость
Feature: F006, F007
Scenarios: SC015, SC017, SC018
"""

from __future__ import annotations

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from model.base_model import Base, BaseModel


class NotificationLogModel(Base, BaseModel):
    __tablename__ = "notification_log"

    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    task_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True, index=True
    )
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    payload_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        Index("ix_notification_log_kind_task", "kind", "task_id"),
    )
