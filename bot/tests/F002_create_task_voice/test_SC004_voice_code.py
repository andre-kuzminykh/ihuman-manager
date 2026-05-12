"""
Тест SC004 — VoiceCode расшифровывает и создаёт задачу.

## Трассируемость
Feature: F002
Scenario: SC004
"""

from unittest.mock import AsyncMock

import pytest

from node.voice.code.voice_code import VoiceCode


@pytest.mark.asyncio
async def test_voice_code_creates_task(mock_state):
    voice_api = AsyncMock()
    voice_api.transcribe = AsyncMock(return_value="Подготовить отчёт до пятницы")
    tasks_api = AsyncMock()
    tasks_api.create = AsyncMock(return_value={"id": 1, "title": "ok", "status": "todo"})

    code = VoiceCode(voice_api=voice_api, tasks_api=tasks_api)
    result = await code.run(
        {"user_id": 42, "audio_bytes": b"abc", "file_name": "v.ogg", "duration": 5}, mock_state
    )
    assert result["answer_name"] == "task_created"
    voice_api.transcribe.assert_awaited_once()
    tasks_api.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_voice_code_empty_audio(mock_state):
    voice_api = AsyncMock()
    tasks_api = AsyncMock()
    code = VoiceCode(voice_api=voice_api, tasks_api=tasks_api)
    result = await code.run(
        {"user_id": 42, "audio_bytes": b"", "file_name": "v.ogg", "duration": 0}, mock_state
    )
    assert result["answer_name"] == "voice_failed"
    voice_api.transcribe.assert_not_called()
    tasks_api.create.assert_not_called()
