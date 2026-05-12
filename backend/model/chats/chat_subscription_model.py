"""
ChatSubscriptionModel — подписка бота на групповой чат/канал.

## Трассируемость
Feature: F005
Scenarios: SC011
"""

from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from model.base_model import Base, BaseModel


class ChatSubscriptionModel(Base, BaseModel):
    __tablename__ = "tg_chats_subscribed"

    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    owner_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (UniqueConstraint("chat_id", name="uq_chat_subscription_chat_id"),)
