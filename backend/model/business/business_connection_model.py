"""
BusinessConnectionModel — связь между Telegram Business аккаунтом и ботом.

## Трассируемость
Feature: F018 — Business account integration
Scenarios: SC036, SC037

Когда пользователь Premium-аккаунта подключает бота через
Settings → Business → Chatbots, Telegram присылает update
`business_connection` с уникальным id и user_id владельца. Это маппинг,
чтобы при получении `business_message` знать, кому слать карточки.
"""

from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from model.base_model import Base, BaseModel


class BusinessConnectionModel(Base, BaseModel):
    __tablename__ = "business_connections"

    business_connection_id: Mapped[str] = mapped_column(String(64), nullable=False)
    owner_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_reply: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint("business_connection_id", name="uq_business_connection_id"),
    )
