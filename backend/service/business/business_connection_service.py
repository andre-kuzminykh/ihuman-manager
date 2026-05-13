"""
BusinessConnectionService — upsert и lookup бизнес-подключений.

## Трассируемость
Feature: F018
Scenarios: SC036, SC037
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import NotFoundError
from model.business.business_connection_model import BusinessConnectionModel
from repository.business.business_connection_repository import (
    BusinessConnectionRepository,
)


class BusinessConnectionService:
    def __init__(self, repo: BusinessConnectionRepository | None = None) -> None:
        self._repo = repo or BusinessConnectionRepository()

    async def upsert(
        self,
        session: AsyncSession,
        *,
        business_connection_id: str,
        owner_user_id: int,
        is_enabled: bool = True,
        can_reply: bool = False,
    ) -> BusinessConnectionModel:
        existing = await self._repo.get_by_connection_id(session, business_connection_id)
        if existing is not None:
            existing.owner_user_id = owner_user_id
            existing.is_enabled = is_enabled
            existing.can_reply = can_reply
            await session.flush()
            await session.refresh(existing)
            return existing
        return await self._repo.create(
            session,
            business_connection_id=business_connection_id,
            owner_user_id=owner_user_id,
            is_enabled=is_enabled,
            can_reply=can_reply,
        )

    async def get_owner(
        self, session: AsyncSession, business_connection_id: str
    ) -> int | None:
        obj = await self._repo.get_by_connection_id(session, business_connection_id)
        if obj is None or not obj.is_enabled:
            return None
        return obj.owner_user_id
