"""
## Трассируемость
Feature: F005
Scenarios: SC012, SC013, SC014
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model.chats.pending_task_model import PendingTaskModel
from repository.base_repository import BaseRepository


class PendingTaskRepository(BaseRepository[PendingTaskModel]):
    def __init__(self) -> None:
        super().__init__(PendingTaskModel)

    async def list_for_owner(
        self, session: AsyncSession, owner_user_id: int, *, only_unapproved: bool = True
    ) -> list[PendingTaskModel]:
        stmt = select(PendingTaskModel).where(
            PendingTaskModel.owner_user_id == owner_user_id
        )
        if only_unapproved:
            stmt = stmt.where(
                PendingTaskModel.approved.is_(False),
                PendingTaskModel.rejected_at.is_(None),
            )
        stmt = stmt.order_by(PendingTaskModel.created_at.desc())
        result = await session.execute(stmt)
        return list(result.scalars().all())
