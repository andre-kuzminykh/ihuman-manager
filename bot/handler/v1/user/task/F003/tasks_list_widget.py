"""
Виджет: /tasks и /favorites — список задач.

## Трассируемость
Feature: F003, F004
Scenarios: SC006, SC009
"""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from callback.tasks_callback import TaskCardCallback
from node.task.answer.task_card_answer import TaskCardAnswer
from node.task.answer.task_list_answer import TaskListAnswer
from service.api.tasks_api import TasksAPI


router = Router(name="task.F003.list")


@router.message(Command("tasks"))
async def on_tasks(message: Message) -> None:
    api = TasksAPI()
    tasks = await api.list(user_id=message.from_user.id) if message.from_user else []
    await TaskListAnswer().run(event=message, user_lang="ru", data={"tasks": tasks})


@router.message(Command("favorites"))
async def on_favorites(message: Message) -> None:
    api = TasksAPI()
    tasks = (
        await api.list(user_id=message.from_user.id, favorite_only=True)
        if message.from_user
        else []
    )
    await TaskListAnswer().run(event=message, user_lang="ru", data={"tasks": tasks})


@router.callback_query(TaskCardCallback.filter())
async def on_task_card(cb: CallbackQuery, callback_data: TaskCardCallback) -> None:
    api = TasksAPI()
    task = await api.get(callback_data.task_id)
    await TaskCardAnswer().run(event=cb, user_lang="ru", data={"task": task})
