"""
TaskRepository — выборки задач.

## Трассируемость
Feature: F001, F003, F004, F006, F007, F009
Scenarios: SC001–SC009, SC015, SC018, SC023
"""

from __future__ import annotations

from datetime import datetime
from typing import Iterable

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from model.directions.direction_model import DirectionModel
from model.enums import TaskStatus
from model.tasks.task_favorite_model import TaskFavoriteModel
from model.tasks.task_model import TaskModel
from repository.base_repository import BaseRepository


class TaskRepository(BaseRepository[TaskModel]):
    def __init__(self) -> None:
        super().__init__(TaskModel)

    async def list_for_user(
        self,
        session: AsyncSession,
        user_id: int,
        *,
        statuses: Iterable[TaskStatus] | None = None,
        deadline_before: datetime | None = None,
        deadline_after: datetime | None = None,
        direction_id: int | None = None,
        favorite_only: bool = False,
        include_deleted: bool = False,
    ) -> list[TaskModel]:
        stmt = select(TaskModel).where(TaskModel.user_id == user_id)
        if not include_deleted:
            stmt = stmt.where(TaskModel.deleted_at.is_(None))
        if statuses:
            stmt = stmt.where(TaskModel.status.in_([s.value for s in statuses]))
        if deadline_before is not None:
            stmt = stmt.where(TaskModel.deadline < deadline_before)
        if deadline_after is not None:
            stmt = stmt.where(TaskModel.deadline >= deadline_after)
        if direction_id is not None:
            stmt = stmt.where(TaskModel.direction_id == direction_id)
        if favorite_only:
            fav_subq = select(TaskFavoriteModel.task_id).where(
                TaskFavoriteModel.user_id == user_id
            )
            fav_dir_subq = (
                select(DirectionModel.id)
                .where(
                    and_(
                        DirectionModel.user_id == user_id,
                        DirectionModel.is_favorite.is_(True),
                    )
                )
            )
            stmt = stmt.where(
                or_(
                    TaskModel.id.in_(fav_subq),
                    TaskModel.direction_id.in_(fav_dir_subq),
                )
            )
        stmt = stmt.order_by(TaskModel.deadline.asc(), TaskModel.id.asc())
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def list_due_in_window(
        self,
        session: AsyncSession,
        *,
        not_after: datetime,
        excluded_statuses: Iterable[TaskStatus] = (TaskStatus.DONE, TaskStatus.CANCELLED),
    ) -> list[TaskModel]:
        stmt = (
            select(TaskModel)
            .where(TaskModel.deleted_at.is_(None))
            .where(TaskModel.deadline <= not_after)
            .where(TaskModel.status.notin_([s.value for s in excluded_statuses]))
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def list_for_todo_promotion(
        self, session: AsyncSession, *, deadline_before: datetime
    ) -> list[TaskModel]:
        stmt = (
            select(TaskModel)
            .where(TaskModel.status == TaskStatus.BACKLOG.value)
            .where(TaskModel.deadline <= deadline_before)
            .where(TaskModel.deleted_at.is_(None))
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
