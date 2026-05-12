"""
VoiceTrigger — скачивает голосовое и кладёт байты в данные для Code.

## Трассируемость
Feature: F002
Scenarios: SC004, SC005
"""

from __future__ import annotations

from io import BytesIO

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.loader import get_bot


class VoiceTrigger:
    async def run(self, message: Message, state: FSMContext) -> dict:
        await state.clear()
        voice = message.voice or message.audio
        if voice is None or message.from_user is None:
            return {"user_id": 0, "audio_bytes": b"", "duration": 0}
        bot = get_bot()
        buffer = BytesIO()
        await bot.download(voice, destination=buffer)
        return {
            "user_id": message.from_user.id,
            "audio_bytes": buffer.getvalue(),
            "duration": getattr(voice, "duration", 0) or 0,
            "file_name": "voice.ogg",
        }
