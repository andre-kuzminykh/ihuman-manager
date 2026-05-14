"""
MessageContextModel — последние сообщения чата (sliding window, BR013).

## Трассируемость
Feature: F005
Scenarios: SC012
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from model.base_model import Base, BaseModel


class MessageContextModel(Base, BaseModel):
    __tablename__ = "message_context"

    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sender_user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    sender_username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sender_first_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    sender_last_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (Index("ix_message_context_chat_sent", "chat_id", "sent_at"),)
