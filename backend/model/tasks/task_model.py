"""
TaskModel — основная сущность задачи.

## Трассируемость
Feature: F001, F002, F003, F005, F006, F007, F008, F009
Scenarios: SC001–SC024

## Бизнес-контекст
Хранит и заголовок, и исходный текст, дедлайн, статус, плановые start/end,
направление и поля состояния (paused_at, completed_at, cancelled_at).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from model.base_model import Base, BaseModel
from model.enums import TaskPriority, TaskSource, TaskStatus


class TaskModel(Base, BaseModel):
    __tablename__ = "tasks"

    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    chat_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    source_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    source_sender_username: Mapped[str | None] = mapped_column(String(64), nullable=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_kind: Mapped[str] = mapped_column(
        String(16), nullable=False, default=TaskSource.TEXT.value
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default=TaskStatus.BACKLOG.value, index=True
    )
    priority: Mapped[str] = mapped_column(
        String(8), nullable=False, default=TaskPriority.MEDIUM.value
    )

    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    planned_start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    planned_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    direction_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("directions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    paused_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_tasks_user_status", "user_id", "status"),
        Index("ix_tasks_user_deadline", "user_id", "deadline"),
    )
