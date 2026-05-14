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
        if message.voice:
            media, file_name = message.voice, "voice.ogg"
        elif message.audio:
            media, file_name = message.audio, "audio.ogg"
        elif message.video_note:
            media, file_name = message.video_note, "video_note.mp4"
        elif message.video:
            media, file_name = message.video, "video.mp4"
        else:
            media, file_name = None, "voice.ogg"
        if media is None or message.from_user is None:
            return {"user_id": 0, "audio_bytes": b"", "duration": 0}
        bot = get_bot()
        buffer = BytesIO()
        await bot.download(media, destination=buffer)
        return {
            "user_id": message.from_user.id,
            "audio_bytes": buffer.getvalue(),
            "duration": getattr(media, "duration", 0) or 0,
            "file_name": file_name,
        }
