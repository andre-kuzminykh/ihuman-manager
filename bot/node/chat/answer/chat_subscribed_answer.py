"""
## Трассируемость
Feature: F005
Scenarios: SC011
"""

from __future__ import annotations

from aiogram.types import Message

from core import vocab


class ChatSubscribedAnswer:
    async def run(self, *, event: Message, user_lang: str = "ru", data: dict) -> None:
        msg = data.get("message") or vocab.CHAT_SUBSCRIBED
        await event.answer(msg)
