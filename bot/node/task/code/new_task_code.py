"""
NewTaskCode — создание задачи + выбор Answer.

## Трассируемость
Feature: F001, F002, F010, F015
Scenarios: SC001, SC002, SC003, SC004, SC025, SC033, SC034
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
            result = await self._api.create_batch(
                user_id=trigger_data["user_id"],
                text=text,
                source_kind=trigger_data.get("source_kind", "text"),
                force=bool(trigger_data.get("force", False)),
            )
        except APIError as exc:
            return {"answer_name": "task_empty_error", "data": {"message": exc.message}}

        tasks: list[dict] = result.get("tasks", []) if isinstance(result, dict) else []
        if not tasks:
            return {"answer_name": "task_empty_error", "data": {"message": "Не нашёл задач в сообщении"}}

        # Дубли молча отбрасываем — пользователю не показываем.
        fresh = [t for t in tasks if not t.get("is_duplicate")]
        if not fresh:
            return {"answer_name": "silent", "data": {}}
        if len(fresh) == 1:
            return {"answer_name": "task_created", "data": {"task": fresh[0]}}
        return {"answer_name": "tasks_created_multi", "data": {"tasks": fresh}}
