"""
## Трассируемость
Feature: F004
Scenarios: SC009, SC010
"""

from __future__ import annotations

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from model.tasks.task_favorite_model import TaskFavoriteModel


class TaskFavoriteRepository:
    async def add(self, session: AsyncSession, *, user_id: int, task_id: int) -> bool:
        exists = await self.exists(session, user_id=user_id, task_id=task_id)
        if exists:
            return False
        session.add(TaskFavoriteModel(user_id=user_id, task_id=task_id))
        await session.flush()
        return True

    async def remove(self, session: AsyncSession, *, user_id: int, task_id: int) -> bool:
        result = await session.execute(
            delete(TaskFavoriteModel).where(
                and_(
                    TaskFavoriteModel.user_id == user_id,
                    TaskFavoriteModel.task_id == task_id,
                )
            )
        )
        return bool(result.rowcount)

    async def exists(self, session: AsyncSession, *, user_id: int, task_id: int) -> bool:
        result = await session.execute(
            select(TaskFavoriteModel).where(
                and_(
                    TaskFavoriteModel.user_id == user_id,
                    TaskFavoriteModel.task_id == task_id,
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def task_ids_for_user(self, session: AsyncSession, user_id: int) -> list[int]:
        result = await session.execute(
            select(TaskFavoriteModel.task_id).where(TaskFavoriteModel.user_id == user_id)
        )
        return list(result.scalars().all())
