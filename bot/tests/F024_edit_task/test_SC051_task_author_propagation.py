"""
SC051 — автор задачи всегда сохраняется и виден на карточке.

Регрессия: «потерял человека» — задача создаётся без 👤-строки,
потому что
  (а) F001/F002 не пробрасывали sender в API, и/или
  (б) MessageIngestService обнулял sender_display при is_self_write.

Сейчас:
  - NewTaskTrigger / VoiceTrigger / F014 кладут sender_user_id /
    sender_username / sender_display в trigger_data;
  - TasksAPI.create_batch + TasksAPI.create транслируют эти поля в JSON;
  - Backend (BatchCreateSchema, TaskCreateSchema) принимает их и
    передаёт в TaskService.create_*;
  - Ingest не стирает sender_display даже когда is_self_write=True.

## Трассируемость
Feature: F001, F002, F005, F014, F024
Scenario: SC051 — автор задачи всегда отображается.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from node.task.trigger.new_task_trigger import NewTaskTrigger
from node.voice.trigger.voice_trigger import VoiceTrigger
from node.task.code.new_task_code import NewTaskCode
from node.voice.code.voice_code import VoiceCode


# ---------- triggers fill sender_* ----------


@pytest.mark.asyncio
async def test_new_task_trigger_fills_sender_from_message_user() -> None:
    state = AsyncMock()
    state.clear = AsyncMock()
    message = MagicMock()
    message.text = "купить молоко"
    message.from_user = MagicMock(
        id=42, username="andre", first_name="Андре", last_name="К."
    )
    data = await NewTaskTrigger().run(message, state)
    assert data["sender_user_id"] == 42
    assert data["sender_username"] == "andre"
    assert data["sender_display"] == "Андре К."


@pytest.mark.asyncio
async def test_new_task_trigger_sender_falls_back_to_username() -> None:
    state = AsyncMock()
    state.clear = AsyncMock()
    message = MagicMock()
    message.text = "x"
    message.from_user = MagicMock(
        id=42, username="andre", first_name=None, last_name=None
    )
    data = await NewTaskTrigger().run(message, state)
    assert data["sender_display"] == "@andre"


@pytest.mark.asyncio
async def test_voice_trigger_fills_sender() -> None:
    state = AsyncMock()
    state.clear = AsyncMock()
    message = MagicMock()
    message.voice = MagicMock(duration=3, file_id="x")
    message.audio = None
    message.video_note = None
    message.video = None
    message.from_user = MagicMock(
        id=7, username="anna", first_name="Анна", last_name="И."
    )
    fake_bot = MagicMock()
    fake_bot.download = AsyncMock()
    with patch("node.voice.trigger.voice_trigger.get_bot", return_value=fake_bot):
        data = await VoiceTrigger().run(message, state)
    assert data["sender_user_id"] == 7
    assert data["sender_username"] == "anna"
    assert data["sender_display"] == "Анна И."


# ---------- codes forward sender_* into create_batch ----------


@pytest.mark.asyncio
async def test_new_task_code_passes_sender_to_create_batch() -> None:
    api = MagicMock()
    api.create_batch = AsyncMock(return_value={
        "tasks": [{"id": 1, "title": "x", "is_duplicate": False}]
    })
    code = NewTaskCode(api=api)
    await code.run({
        "user_id": 42,
        "text": "x",
        "source_kind": "text",
        "sender_user_id": 42,
        "sender_username": "andre",
        "sender_display": "Андре К.",
    }, AsyncMock())
    kw = api.create_batch.call_args.kwargs
    assert kw["source_sender_user_id"] == 42
    assert kw["source_sender_username"] == "andre"
    assert kw["source_sender_display"] == "Андре К."


@pytest.mark.asyncio
async def test_voice_code_passes_sender_to_create_batch() -> None:
    voice_api = MagicMock()
    voice_api.transcribe = AsyncMock(return_value="купить молоко")
    tasks_api = MagicMock()
    tasks_api.create_batch = AsyncMock(return_value={
        "tasks": [{"id": 1, "title": "x", "is_duplicate": False}]
    })
    code = VoiceCode(voice_api=voice_api, tasks_api=tasks_api)
    await code.run({
        "user_id": 7,
        "audio_bytes": b"abc",
        "file_name": "v.ogg",
        "duration": 1,
        "sender_user_id": 7,
        "sender_username": "anna",
        "sender_display": "Анна И.",
    }, AsyncMock())
    kw = tasks_api.create_batch.call_args.kwargs
    assert kw["source_sender_user_id"] == 7
    assert kw["source_sender_username"] == "anna"
    assert kw["source_sender_display"] == "Анна И."
