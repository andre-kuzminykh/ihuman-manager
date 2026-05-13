"""
Виджет: переход статуса задачи через inline-кнопки.

## Трассируемость
Feature: F003
Scenarios: SC006, SC008
"""

from __future__ import annotations

from aiogram import Router
from aiogram.types import CallbackQuery

from callback.tasks_callback import TaskActionCallback
from node.task.answer.invalid_transition_answer import InvalidTransitionAnswer
from node.task.answer.task_card_answer import TaskCardAnswer
from service.api.base_api import APIError
from service.api.tasks_api import TasksAPI


router = Router(name="task.F003.status")

_STATUS_MAP = {
    "start": "in_progress",
    "pause": "paused",
    "block": "blocked",
    "done": "done",
    "cancel": "cancelled",
    "reopen": "todo",  # done/cancelled → todo
}

_ANSWER_REGISTRY = {
    "task_card": TaskCardAnswer(),
    "invalid_transition": InvalidTransitionAnswer(),
}


@router.callback_query(TaskActionCallback.filter())
async def on_task_action(cb: CallbackQuery, callback_data: TaskActionCallback) -> None:
    api = TasksAPI()
    action = callback_data.action

    if action in _STATUS_MAP:
        try:
            task = await api.transition_status(
                callback_data.task_id,
                to=_STATUS_MAP[action],
                changed_by=cb.from_user.id if cb.from_user else None,
            )
        except APIError as exc:
            await _ANSWER_REGISTRY["invalid_transition"].run(
                event=cb, user_lang="ru", data={"message": exc.message}
            )
            return
        await _ANSWER_REGISTRY["task_card"].run(event=cb, user_lang="ru", data={"task": task})
        return

    if action in {"favorite", "unfavorite"}:
        # делегируем favorite_widget — там обрабатывается отдельно
        return

    await cb.answer()
