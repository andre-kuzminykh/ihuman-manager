"""
PendingTaskModel — черновик задачи в ожидании апрува из чата.

## Трассируемость
Feature: F005
Scenarios: SC012, SC013, SC014

draft хранит структурированную выжимку (title, deadline, direction_id и пр.) в JSONB.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from model.base_model import Base, BaseModel


class PendingTaskModel(Base, BaseModel):
    __tablename__ = "pending_tasks"

    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    owner_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)

    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    source_sender: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source_chat_username: Mapped[str | None] = mapped_column(String(80), nullable=True)
    draft: Mapped[dict] = mapped_column(JSONB, nullable=False)

    is_auto_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_task_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
