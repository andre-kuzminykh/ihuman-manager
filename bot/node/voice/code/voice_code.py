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
            task = await self._tasks_api.create(
                user_id=trigger_data["user_id"], text=text, source_kind="voice"
            )
        except APIError as exc:
            return {"answer_name": "voice_failed", "data": {"message": exc.message}}
        return {"answer_name": "task_created", "data": {"task": task, "transcribed_text": text}}
