"""
Утилита: скачать голос/аудио из Telegram сообщения и пропустить через Whisper.

## Трассируемость
Feature: F021 — голос в чатах/business тоже идёт через ingest pipeline.
"""

from __future__ import annotations

import logging
from io import BytesIO

from aiogram.types import Message

from core.loader import get_bot
from service.api.voice_api import VoiceAPI


log = logging.getLogger("voice_helper")


async def transcribe_message_voice(message: Message) -> str | None:
    """Если в сообщении есть voice/audio/video_note — скачать и расшифровать.
    Видео-кружочки (video_note) — mp4 контейнер, OpenAI принимает.
    Возвращает строку или None.
    """
    if message.voice:
        media = message.voice
        file_name = "voice.ogg"
    elif message.audio:
        media = message.audio
        file_name = "audio.ogg"
    elif message.video_note:
        media = message.video_note
        file_name = "video_note.mp4"
    elif message.video:
        media = message.video
        file_name = "video.mp4"
    else:
        return None
    try:
        bot = get_bot()
        buf = BytesIO()
        await bot.download(media, destination=buf)
        text = await VoiceAPI().transcribe(
            audio_bytes=buf.getvalue(),
            file_name=file_name,
        )
    except Exception:
        log.exception("voice/video transcribe failed")
        return None
    return (text or "").strip() or None
