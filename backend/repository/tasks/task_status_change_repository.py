"""
## Трассируемость
Feature: F003
Scenarios: SC006, SC007
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from model.tasks.task_status_change_model import TaskStatusChangeModel


class TaskStatusChangeRepository:
    async def add(
        self,
        session: AsyncSession,
        *,
        task_id: int,
        from_status: str | None,
        to_status: str,
        changed_by: int | None = None,
        reason: str | None = None,
    ) -> TaskStatusChangeModel:
        obj = TaskStatusChangeModel(
            task_id=task_id,
            from_status=from_status,
            to_status=to_status,
            changed_by=changed_by,
            reason=reason,
        )
        session.add(obj)
        await session.flush()
        return obj
