"""
NewTaskCode — создание задачи + выбор Answer.

## Трассируемость
Feature: F001, F002
Scenarios: SC001, SC002, SC003, SC004
"""

from __future__ import annotations

from aiogram.fsm.context import FSMContext

from service.api.base_api import APIError
from service.api.tasks_api import TasksAPI


class NewTaskCode:
    def __init__(self, api: TasksAPI | None = None) -> None:
        self._api = api or TasksAPI()

    async def run(self, trigger_data: dict, state: FSMContext) -> dict:
        text = (trigger_data.get("text") or "").strip()
        if not text:
            return {"answer_name": "task_empty_error", "data": {}}
        try:
            task = await self._api.create(
                user_id=trigger_data["user_id"],
                text=text,
                source_kind=trigger_data.get("source_kind", "text"),
                force=bool(trigger_data.get("force", False)),
            )
        except APIError as exc:
            if exc.status_code == 422:
                return {"answer_name": "task_empty_error", "data": {"message": exc.message}}
            return {"answer_name": "task_empty_error", "data": {"message": exc.message}}
        if task.get("is_duplicate"):
            return {
                "answer_name": "duplicate_found",
                "data": {"task": task, "raw_text": text},
            }
        return {"answer_name": "task_created", "data": {"task": task}}
