"""
VoiceCode — расшифровка + создание задачи.

## Трассируемость
Feature: F002
Scenarios: SC004, SC005
"""

from __future__ import annotations

from aiogram.fsm.context import FSMContext

from service.api.base_api import APIError
from service.api.tasks_api import TasksAPI
from service.api.voice_api import VoiceAPI


class VoiceCode:
    def __init__(
        self,
        voice_api: VoiceAPI | None = None,
        tasks_api: TasksAPI | None = None,
    ) -> None:
        self._voice_api = voice_api or VoiceAPI()
        self._tasks_api = tasks_api or TasksAPI()

    async def run(self, trigger_data: dict, state: FSMContext) -> dict:
        audio = trigger_data.get("audio_bytes")
        if not audio:
            return {"answer_name": "voice_failed", "data": {}}
        try:
            text = await self._voice_api.transcribe(
                audio_bytes=audio, file_name=trigger_data.get("file_name", "voice.ogg")
            )
        except Exception:
            return {"answer_name": "voice_failed", "data": {}}
        if not text.strip():
            return {"answer_name": "voice_failed", "data": {}}
        try:
            result = await self._tasks_api.create_batch(
                user_id=trigger_data["user_id"],
                text=text,
                source_kind="voice",
                source_sender_user_id=trigger_data.get("sender_user_id"),
                source_sender_username=trigger_data.get("sender_username"),
                source_sender_display=trigger_data.get("sender_display"),
            )
        except APIError as exc:
            return {"answer_name": "voice_failed", "data": {"message": exc.message}}

        tasks: list[dict] = result.get("tasks", []) if isinstance(result, dict) else []
        if not tasks:
            return {"answer_name": "voice_failed", "data": {"message": "Не нашёл задач в голосе"}}

        fresh = [t for t in tasks if not t.get("is_duplicate")]
        if not fresh:
            return {"answer_name": "silent", "data": {}}
        if len(fresh) == 1:
            return {
                "answer_name": "task_created",
                "data": {"task": fresh[0], "transcribed_text": text},
            }
        return {
            "answer_name": "tasks_created_multi",
            "data": {"tasks": fresh, "transcribed_text": text},
        }
