"""
## Трассируемость
Feature: F001
Scenarios: SC003
"""

from __future__ import annotations

from aiogram.types import Message

from core import vocab


class TaskEmptyErrorAnswer:
    async def run(self, *, event: Message, user_lang: str = "ru", data: dict) -> None:
        await event.answer(data.get("message") or vocab.EMPTY_TEXT)
