"""
## Трассируемость
Feature: F005
Scenarios: SC011
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model.chats.chat_subscription_model import ChatSubscriptionModel
from repository.base_repository import BaseRepository


class ChatSubscriptionRepository(BaseRepository[ChatSubscriptionModel]):
    def __init__(self) -> None:
        super().__init__(ChatSubscriptionModel)

    async def get_by_chat_id(
        self, session: AsyncSession, chat_id: int
    ) -> ChatSubscriptionModel | None:
        stmt = select(ChatSubscriptionModel).where(ChatSubscriptionModel.chat_id == chat_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
