"""
TaskCardAnswer — обновление карточки задачи (после изменения статуса/избранного).

## Трассируемость
Feature: F003, F004, F008
Scenarios: SC006, SC007, SC009, SC010, SC016, SC020
"""

from __future__ import annotations

from aiogram.types import CallbackQuery, Message

from node.task.answer.task_created_answer import build_task_card_kb, render_task_card


class TaskCardAnswer:
    async def run(self, *, event: Message | CallbackQuery, user_lang: str = "ru", data: dict) -> None:
        task = data["task"]
        # без префикса — только содержимое карточки.
        text = render_task_card(task)
        kb = build_task_card_kb(task)
        if isinstance(event, CallbackQuery):
            if event.message is not None:
                await event.message.edit_text(
                    text, reply_markup=kb, disable_web_page_preview=True
                )
            await event.answer()
        else:
            await event.answer(text, reply_markup=kb, disable_web_page_preview=True)
