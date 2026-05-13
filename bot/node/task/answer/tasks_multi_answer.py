"""
TasksMultiAnswer — отвечает сводным сообщением и набором карточек,
когда из одного входа извлекли несколько задач.

## Трассируемость
Feature: F015
Scenarios: SC033
"""

from __future__ import annotations

from aiogram.types import Message

from core import vocab
from node.task.answer.task_created_answer import build_task_card_kb, render_task_card


class TasksMultiAnswer:
    async def run(self, *, event: Message, user_lang: str = "ru", data: dict) -> None:
        tasks: list[dict] = data.get("tasks", [])
        await event.answer(vocab.MULTI_TASKS_FOUND.format(count=len(tasks)))
        for task in tasks:
            prefix = "📌 Дубль" if task.get("is_duplicate") else vocab.TASK_CREATED
            await event.answer(
                render_task_card(task, title_prefix=prefix),
                reply_markup=build_task_card_kb(task),
            )
