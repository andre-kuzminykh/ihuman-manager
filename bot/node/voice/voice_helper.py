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
    """Если в сообщении есть voice/audio — скачать и расшифровать через Whisper.
    Возвращает строку или None. Лимит — 60 сек длительности (берётся как есть,
    лимит — у самого Whisper API).
    """
    voice = message.voice or message.audio
    if voice is None:
        return None
    try:
        bot = get_bot()
        buf = BytesIO()
        await bot.download(voice, destination=buf)
        text = await VoiceAPI().transcribe(
            audio_bytes=buf.getvalue(),
            file_name="voice.ogg" if message.voice else "audio.ogg",
        )
    except Exception:
        log.exception("voice transcribe failed")
        return None
    return (text or "").strip() or None
