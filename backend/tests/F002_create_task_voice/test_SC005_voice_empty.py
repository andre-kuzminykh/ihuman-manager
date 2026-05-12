"""
Тест SC005 — пустая расшифровка → HTTP 422.

## Трассируемость
Feature: F002
Scenario: SC005
"""

import pytest

from core.exceptions import ValidationError
from service.voice.voice_service import VoiceService


@pytest.mark.asyncio
async def test_empty_audio_raises(client, monkeypatch):
    async def fake_transcribe(self, *, audio_bytes, file_name="voice.ogg"):
        raise ValidationError("Не удалось распознать голос")

    monkeypatch.setattr(VoiceService, "transcribe", fake_transcribe)

    files = {"file": ("voice.ogg", b"", "audio/ogg")}
    response = await client.post("/api/v1/voice/transcribe", files=files)
    assert response.status_code == 422
    assert "Не удалось" in response.json()["message"]
