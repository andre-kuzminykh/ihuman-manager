"""
## Трассируемость
Feature: F003
Scenarios: SC008
"""

from __future__ import annotations

from aiogram.types import CallbackQuery, Message

from core import vocab


class InvalidTransitionAnswer:
    async def run(self, *, event: Message | CallbackQuery, user_lang: str = "ru", data: dict) -> None:
        text = data.get("message") or vocab.INVALID_TRANSITION
        if isinstance(event, CallbackQuery):
            await event.answer(text, show_alert=True)
        else:
            await event.answer(text)
