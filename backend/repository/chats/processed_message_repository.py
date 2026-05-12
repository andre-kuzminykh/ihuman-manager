"""
## Трассируемость
Feature: F005
Scenarios: SC012, SC013
"""

from __future__ import annotations

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from model.chats.processed_message_model import ProcessedMessageModel


class ProcessedMessageRepository:
    async def is_processed(
        self, session: AsyncSession, chat_id: int, message_id: int
    ) -> bool:
        stmt = select(ProcessedMessageModel).where(
            and_(
                ProcessedMessageModel.chat_id == chat_id,
                ProcessedMessageModel.message_id == message_id,
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def mark_processed(
        self, session: AsyncSession, chat_id: int, message_id: int
    ) -> None:
        session.add(ProcessedMessageModel(chat_id=chat_id, message_id=message_id))
        await session.flush()
