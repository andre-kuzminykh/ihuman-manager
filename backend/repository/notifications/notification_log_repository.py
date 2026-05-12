"""
## Трассируемость
Feature: F006, F007
Scenarios: SC015, SC017, SC018
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from model.notifications.notification_log_model import NotificationLogModel


class NotificationLogRepository:
    async def add(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        task_id: int | None,
        kind: str,
        payload_hash: str | None = None,
    ) -> NotificationLogModel:
        obj = NotificationLogModel(
            user_id=user_id,
            task_id=task_id,
            kind=kind,
            payload_hash=payload_hash,
        )
        session.add(obj)
        await session.flush()
        return obj

    async def exists_for_task(
        self, session: AsyncSession, *, task_id: int, kind: str
    ) -> bool:
        stmt = select(NotificationLogModel).where(
            and_(NotificationLogModel.task_id == task_id, NotificationLogModel.kind == kind)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def exists_for_user_on_date(
        self, session: AsyncSession, *, user_id: int, kind: str, date_value: datetime
    ) -> bool:
        stmt = select(NotificationLogModel).where(
            and_(
                NotificationLogModel.user_id == user_id,
                NotificationLogModel.kind == kind,
                NotificationLogModel.created_at >= date_value,
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None
