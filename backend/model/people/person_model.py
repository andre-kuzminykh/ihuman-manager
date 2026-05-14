"""
PersonModel — контакт владельца бота.

## Трассируемость
Feature: F020 — People (контакты)
Scenarios: SC040, SC041

Хранит всю инфу из Telegram, которая прилетает в `from_user` любого
сообщения: telegram id, username, first/last name, is_bot, lang, premium.
Плюс агрегаты — last_seen_at, message_count, и поле notes для заметок.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from model.base_model import Base, BaseModel


class PersonModel(Base, BaseModel):
    __tablename__ = "people"

    telegram_user_id: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True, index=True
    )
    username: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    first_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    language_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("telegram_user_id", name="uq_people_tg_user_id"),
    )
