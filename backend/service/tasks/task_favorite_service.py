"""
TaskFavoriteService.

## Трассируемость
Feature: F004
Scenarios: SC009, SC010
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import NotFoundError
from repository.tasks.task_favorite_repository import TaskFavoriteRepository
from repository.tasks.task_repository import TaskRepository


class TaskFavoriteService:
    def __init__(
        self,
        repo: TaskFavoriteRepository | None = None,
        task_repo: TaskRepository | None = None,
    ) -> None:
        self._repo = repo or TaskFavoriteRepository()
        self._task_repo = task_repo or TaskRepository()

    async def add(self, session: AsyncSession, *, user_id: int, task_id: int) -> bool:
        task = await self._task_repo.get_by_id(session, task_id)
        if task is None:
            raise NotFoundError(f"Task {task_id} not found")
        return await self._repo.add(session, user_id=user_id, task_id=task_id)

    async def remove(self, session: AsyncSession, *, user_id: int, task_id: int) -> bool:
        return await self._repo.remove(session, user_id=user_id, task_id=task_id)
