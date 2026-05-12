"""
VoiceService — расшифровка голосовых сообщений (Whisper).

## Трассируемость
Feature: F002
Scenarios: SC004, SC005

## Зависимости
- OpenAI Whisper (`WHISPER_MODEL`)
"""

from __future__ import annotations

import io
import logging

from core.config import config
from core.exceptions import ValidationError


log = logging.getLogger(__name__)


class VoiceService:
    def __init__(
        self, openai_api_key: str | None = None, whisper_model: str | None = None
    ) -> None:
        self._api_key = openai_api_key if openai_api_key is not None else config.OPENAI_API_KEY
        self._model = whisper_model or config.WHISPER_MODEL
        self._client = None
        if self._api_key:
            try:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(api_key=self._api_key)
            except Exception as exc:  # pragma: no cover
                log.warning("OpenAI SDK init failed: %s", exc)
                self._client = None

    async def transcribe(self, *, audio_bytes: bytes, file_name: str = "voice.ogg") -> str:
        if not audio_bytes:
            raise ValidationError("Не удалось распознать голос")
        if self._client is None:
            raise ValidationError(
                "VoiceService недоступен: задайте OPENAI_API_KEY"
            )
        buf = io.BytesIO(audio_bytes)
        buf.name = file_name
        try:
            result = await self._client.audio.transcriptions.create(
                model=self._model,
                file=buf,
                response_format="text",
            )
        except Exception as exc:  # pragma: no cover
            log.exception("Whisper transcribe failed")
            raise ValidationError("Не удалось распознать голос") from exc
        text = (result if isinstance(result, str) else getattr(result, "text", "")) or ""
        text = text.strip()
        if not text:
            raise ValidationError("Не удалось распознать голос")
        return text
