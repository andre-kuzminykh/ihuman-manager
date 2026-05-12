"""
Тест SC004 — голос распознан → создаётся задача.

## Трассируемость
Feature: F002
Scenario: SC004
"""

from unittest.mock import AsyncMock

import pytest

from service.voice.voice_service import VoiceService


@pytest.mark.asyncio
async def test_voice_creates_task(client, monkeypatch):
    async def fake_transcribe(self, *, audio_bytes, file_name="voice.ogg"):
        return "Подготовить отчёт до пятницы"

    monkeypatch.setattr(VoiceService, "transcribe", fake_transcribe)

    files = {"file": ("voice.ogg", b"\x00\x01\x02\x03", "audio/ogg")}
    response = await client.post("/api/v1/voice/transcribe", files=files)
    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "Подготовить отчёт до пятницы"

    response = await client.post(
        "/api/v1/tasks",
        json={"user_id": 42, "text": body["text"], "source_kind": "voice"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["source_kind"] == "voice"
