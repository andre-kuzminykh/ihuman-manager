"""
ProcessedMessageModel — реестр обработанных сообщений (дедуп, BR016).

## Трассируемость
Feature: F005
Scenarios: SC012, SC013
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from model.base_model import Base, _utcnow


class ProcessedMessageModel(Base):
    __tablename__ = "processed_tg_messages"

    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    __table_args__ = (PrimaryKeyConstraint("chat_id", "message_id"),)
