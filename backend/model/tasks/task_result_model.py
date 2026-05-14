"""
TaskResultModel — артефакт результата задачи.

## Трассируемость
Feature: F022 — результаты задач
Scenarios: SC043

После нажатия ✅ Готово к задаче можно прикрепить:
- текст / ссылку (kind='text')
- голосовое (kind='voice'; content — расшифровка Whisper, file_id — original)
- файл / документ (kind='file'; content — caption или filename, file_id — TG file_id)
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from model.base_model import Base, _utcnow


class TaskResultModel(Base):
    __tablename__ = "task_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    added_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
