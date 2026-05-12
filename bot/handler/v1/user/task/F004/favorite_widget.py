"""
Виджет: добавить/убрать ⭐ через callback.

## Трассируемость
Feature: F004
Scenarios: SC009, SC010
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from callback.tasks_callback import TaskActionCallback
from node.task.answer.task_card_answer import TaskCardAnswer
from service.api.tasks_api import TasksAPI


router = Router(name="task.F004.favorite")


@router.callback_query(TaskActionCallback.filter(F.action.in_({"favorite", "unfavorite"})))
async def on_favorite(cb: CallbackQuery, callback_data: TaskActionCallback) -> None:
    api = TasksAPI()
    user_id = cb.from_user.id if cb.from_user else 0
    if callback_data.action == "favorite":
        await api.add_favorite(callback_data.task_id, user_id)
    else:
        await api.remove_favorite(callback_data.task_id, user_id)
    task = await api.get(callback_data.task_id)
    await TaskCardAnswer().run(event=cb, user_lang="ru", data={"task": task})
