"""
Виджет: создание задачи голосом.

## Трассируемость
Feature: F002
Scenarios: SC004, SC005
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from node.task.answer.duplicate_found_answer import DuplicateFoundAnswer
from node.task.answer.task_created_answer import TaskCreatedAnswer
from node.task.answer.tasks_multi_answer import TasksMultiAnswer
from node.voice.answer.voice_failed_answer import VoiceFailedAnswer
from node.voice.code.voice_code import VoiceCode
from node.voice.trigger.voice_trigger import VoiceTrigger


router = Router(name="voice.F002")

_ANSWER_REGISTRY = {
    "task_created": TaskCreatedAnswer(),
    "voice_failed": VoiceFailedAnswer(),
    "duplicate_found": DuplicateFoundAnswer(),
    "tasks_created_multi": TasksMultiAnswer(),
}


@router.message(F.chat.type == ChatType.PRIVATE, F.voice)
@router.message(F.chat.type == ChatType.PRIVATE, F.audio)
async def on_voice(message: Message, state: FSMContext) -> None:
    trigger = VoiceTrigger()
    trigger_data = await trigger.run(message, state)
    code = VoiceCode()
    code_result = await code.run(trigger_data, state)
    answer_name = code_result["answer_name"]
    if answer_name == "silent":
        return
    answer = _ANSWER_REGISTRY.get(answer_name)
    if answer is None:
        return
    await answer.run(event=message, user_lang="ru", data=code_result["data"])
