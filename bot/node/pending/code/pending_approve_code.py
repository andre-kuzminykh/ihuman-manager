"""
PendingApproveCode — обработка кнопок 'approve', 'reject' на карточке-согласовании.

## Трассируемость
Feature: F005
Scenarios: SC012, SC013, SC014
"""

from __future__ import annotations

from service.api.base_api import APIError
from service.api.pending_tasks_api import PendingTasksAPI
from service.api.tasks_api import TasksAPI


class PendingApproveCode:
    def __init__(
        self,
        pending_api: PendingTasksAPI | None = None,
        tasks_api: TasksAPI | None = None,
    ) -> None:
        self._pending_api = pending_api or PendingTasksAPI()
        self._tasks_api = tasks_api or TasksAPI()

    async def approve(self, pending_id: int) -> dict:
        try:
            pending = await self._pending_api.approve(pending_id)
        except APIError as exc:
            return {"answer_name": "pending_error", "data": {"message": exc.message}}
        task_id = pending.get("created_task_id")
        if not task_id:
            return {"answer_name": "pending_error", "data": {"message": "Task not created"}}
        task = await self._tasks_api.get(task_id)
        return {"answer_name": "task_created", "data": {"task": task, "from_pending": True}}

    async def reject(self, pending_id: int) -> dict:
        try:
            await self._pending_api.reject(pending_id)
        except APIError as exc:
            return {"answer_name": "pending_error", "data": {"message": exc.message}}
        return {"answer_name": "pending_rejected", "data": {"pending_id": pending_id}}
