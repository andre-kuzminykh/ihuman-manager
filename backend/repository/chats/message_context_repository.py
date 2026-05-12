"""
## Трассируемость
Feature: F005
Scenarios: SC012, SC013
"""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from model.chats.message_context_model import MessageContextModel
from repository.base_repository import BaseRepository


class MessageContextRepository(BaseRepository[MessageContextModel]):
    def __init__(self) -> None:
        super().__init__(MessageContextModel)

    async def latest_for_chat(
        self, session: AsyncSession, chat_id: int, limit: int = 10
    ) -> list[MessageContextModel]:
        stmt = (
            select(MessageContextModel)
            .where(MessageContextModel.chat_id == chat_id)
            .order_by(MessageContextModel.sent_at.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        items = list(result.scalars().all())
        items.reverse()
        return items

    async def prune_old(self, session: AsyncSession, chat_id: int, keep: int = 10) -> int:
        latest = await self.latest_for_chat(session, chat_id, keep)
        if not latest:
            return 0
        keep_ids = [item.id for item in latest]
        result = await session.execute(
            delete(MessageContextModel)
            .where(MessageContextModel.chat_id == chat_id)
            .where(MessageContextModel.id.notin_(keep_ids))
        )
        return result.rowcount or 0
