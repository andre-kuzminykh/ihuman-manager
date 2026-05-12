"""
Виджет: быстрые команды /today /overdue /active.

## Трассируемость
Feature: F012
Scenarios: SC029, SC030
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytz
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from core import vocab
from node.task.answer.task_list_answer import TaskListAnswer
from service.api.tasks_api import TasksAPI


router = Router(name="task.F012.shortcuts")

MSK = pytz.timezone("Europe/Moscow")


def _today_window(now: datetime | None = None) -> tuple[datetime, datetime]:
    n = (now or datetime.now(MSK)).astimezone(MSK)
    start = n.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1) - timedelta(microseconds=1)
    return start, end


@router.message(Command("today"))
async def on_today(message: Message) -> None:
    if message.from_user is None:
        return
    api = TasksAPI()
    start, end = _today_window()
    tasks = await api.list(
        user_id=message.from_user.id,
        status=["backlog", "todo", "in_progress", "paused", "blocked"],
        deadline_after=start,
        deadline_before=end + timedelta(microseconds=1),
    )
    if not tasks:
        await message.answer(vocab.NO_TASKS_TODAY)
        return
    await TaskListAnswer().run(event=message, user_lang="ru", data={"tasks": tasks})


@router.message(Command("overdue"))
async def on_overdue(message: Message) -> None:
    if message.from_user is None:
        return
    api = TasksAPI()
    now = datetime.now(MSK)
    tasks = await api.list(
        user_id=message.from_user.id,
        status=["backlog", "todo", "in_progress", "paused", "blocked"],
        deadline_before=now,
    )
    if not tasks:
        await message.answer(vocab.NO_OVERDUE)
        return
    await TaskListAnswer().run(event=message, user_lang="ru", data={"tasks": tasks})


@router.message(Command("active"))
async def on_active(message: Message) -> None:
    if message.from_user is None:
        return
    api = TasksAPI()
    tasks = await api.list(
        user_id=message.from_user.id,
        status=["todo", "in_progress", "blocked"],
    )
    if not tasks:
        await message.answer(vocab.NO_ACTIVE)
        return
    await TaskListAnswer().run(event=message, user_lang="ru", data={"tasks": tasks})
