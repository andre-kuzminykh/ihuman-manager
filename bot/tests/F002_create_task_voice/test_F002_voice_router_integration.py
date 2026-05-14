"""
F002 voice handler integration tests.

Locks in the router-level wiring after adding StateFilter(default_state):
- voice/audio/video_note/video в DM при отсутствии FSM-состояния (raw_state=None)
  должны попадать в on_voice;
- эти же сообщения при FSM=TaskEditStates.main НЕ должны попадать в F002 —
  они перехватываются F024;
- сообщение пользователя удаляется после обработки.

## Трассируемость
Feature: F002, F024
Scenarios: SC004, BR073 (StateFilter belt-and-braces).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state

from handler.v1.user.voice.F002 import voice_widget as vw


@pytest.mark.asyncio
async def test_state_filter_matches_when_no_state_set() -> None:
    """raw_state=None (никогда не входил в FSM) — фильтр должен пропускать."""
    f = StateFilter(default_state)
    assert await f(MagicMock(), raw_state=None) is True


@pytest.mark.asyncio
async def test_state_filter_blocks_when_in_edit_state() -> None:
    """raw_state='TaskEditStates:main' — фильтр НЕ пропускает в F002."""
    f = StateFilter(default_state)
    assert await f(MagicMock(), raw_state="TaskEditStates:main") is False


@pytest.mark.asyncio
async def test_on_voice_deletes_user_message_and_creates_task() -> None:
    """Голос в DM → транскрипция → создаётся задача → исходное сообщение
    удалено, прислана карточка."""
    message = AsyncMock()
    message.delete = AsyncMock()
    state = AsyncMock()

    fake_trigger = MagicMock()
    fake_trigger.run = AsyncMock(return_value={"text": "купить молоко"})
    fake_code = MagicMock()
    fake_code.run = AsyncMock(return_value={
        "answer_name": "task_created",
        "data": {"task": {"id": 1, "title": "купить молоко"}},
    })
    fake_answer = AsyncMock()

    with patch.object(vw, "VoiceTrigger", return_value=fake_trigger), \
         patch.object(vw, "VoiceCode", return_value=fake_code), \
         patch.dict(vw._ANSWER_REGISTRY, {"task_created": fake_answer}):
        await vw.on_voice(message, state)

    fake_trigger.run.assert_awaited_once()
    fake_code.run.assert_awaited_once()
    message.delete.assert_awaited_once()
    fake_answer.run.assert_awaited_once()


@pytest.mark.asyncio
async def test_on_voice_silent_answer_still_deletes_user_message() -> None:
    """Если decision='silent' (дубль и т.п.) — карточка не шлётся,
    но сообщение пользователя всё равно удаляется."""
    message = AsyncMock()
    message.delete = AsyncMock()
    state = AsyncMock()

    fake_trigger = MagicMock()
    fake_trigger.run = AsyncMock(return_value={"text": "..."})
    fake_code = MagicMock()
    fake_code.run = AsyncMock(return_value={"answer_name": "silent", "data": {}})

    with patch.object(vw, "VoiceTrigger", return_value=fake_trigger), \
         patch.object(vw, "VoiceCode", return_value=fake_code):
        await vw.on_voice(message, state)

    message.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_router_registers_voice_audio_video_note_and_video() -> None:
    """Все 4 декоратора зарегистрировали хендлер: voice, audio, video_note, video.
    Регрессия: если кто-то случайно удалит один из декораторов, тест отловит."""
    handlers = vw.router.message.handlers
    # Должно быть как минимум 4 регистрации on_voice.
    on_voice_handlers = [h for h in handlers if h.callback is vw.on_voice]
    assert len(on_voice_handlers) >= 4
