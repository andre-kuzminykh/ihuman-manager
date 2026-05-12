"""
## Трассируемость
Feature: F002
Scenarios: SC005
"""

from __future__ import annotations

from aiogram.types import Message

from core import vocab


class VoiceFailedAnswer:
    async def run(self, *, event: Message, user_lang: str = "ru", data: dict) -> None:
        await event.answer(data.get("message") or vocab.VOICE_FAILED)
