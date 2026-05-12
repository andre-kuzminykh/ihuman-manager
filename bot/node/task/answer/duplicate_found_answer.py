"""
DuplicateFoundAnswer — карточка «уже есть похожая задача».

## Трассируемость
Feature: F010
Scenarios: SC025, SC026
"""

from __future__ import annotations

from aiogram.types import Message

from core import vocab
from node.task.answer.task_created_answer import build_task_card_kb, render_task_card


class DuplicateFoundAnswer:
    async def run(self, *, event: Message, user_lang: str = "ru", data: dict) -> None:
        task = data["task"]
        text = (
            f"⚠️ {vocab.DUPLICATE_FOUND}.\n\n"
            f"{render_task_card(task, title_prefix='🔁 Уже есть')}\n\n"
            "Чтобы всё равно завести, используй "
            "<code>/task &lt;title&gt; | &lt;deadline&gt; | &lt;direction&gt;</code> "
            "— ручной ввод обходит дедуп."
        )
        await event.answer(text, reply_markup=build_task_card_kb(task))
