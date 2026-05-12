"""
ChatSubscriptionService.

## Трассируемость
Feature: F005
Scenarios: SC011
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import NotFoundError
from model.chats.chat_subscription_model import ChatSubscriptionModel
from repository.chats.chat_subscription_repository import ChatSubscriptionRepository


class ChatSubscriptionService:
    def __init__(self, repo: ChatSubscriptionRepository | None = None) -> None:
        self._repo = repo or ChatSubscriptionRepository()

    async def subscribe(
        self,
        session: AsyncSession,
        *,
        chat_id: int,
        owner_user_id: int,
        title: str | None = None,
    ) -> ChatSubscriptionModel:
        existing = await self._repo.get_by_chat_id(session, chat_id)
        if existing is not None:
            existing.owner_user_id = owner_user_id
            existing.enabled = True
            if title is not None:
                existing.title = title
            await session.flush()
            await session.refresh(existing)
            return existing
        return await self._repo.create(
            session,
            chat_id=chat_id,
            owner_user_id=owner_user_id,
            title=title,
            enabled=True,
        )

    async def unsubscribe(self, session: AsyncSession, chat_id: int) -> None:
        existing = await self._repo.get_by_chat_id(session, chat_id)
        if existing is None:
            raise NotFoundError("Subscription not found")
        existing.enabled = False
        await session.flush()

    async def get_active(
        self, session: AsyncSession, chat_id: int
    ) -> ChatSubscriptionModel | None:
        sub = await self._repo.get_by_chat_id(session, chat_id)
        if sub is None or not sub.enabled:
            return None
        return sub
