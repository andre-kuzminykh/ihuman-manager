"""
Виджет: создание задачи текстом.

## Трассируемость
Feature: F001
Scenarios: SC001, SC002, SC003

Triggers:
- /new <text>
- любое DM-сообщение, не являющееся командой, в личке боту.
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from node.task.answer.duplicate_found_answer import DuplicateFoundAnswer
from node.task.answer.task_created_answer import TaskCreatedAnswer
from node.task.answer.task_empty_error_answer import TaskEmptyErrorAnswer
from node.task.answer.tasks_multi_answer import TasksMultiAnswer
from node.task.code.new_task_code import NewTaskCode
from node.task.trigger.new_task_trigger import NewTaskTrigger


router = Router(name="task.F001.new")

_ANSWER_REGISTRY = {
    "task_created": TaskCreatedAnswer(),
    "task_empty_error": TaskEmptyErrorAnswer(),
    "duplicate_found": DuplicateFoundAnswer(),
    "tasks_created_multi": TasksMultiAnswer(),
}


@router.message(Command("new"))
async def on_new_command(message: Message, state: FSMContext) -> None:
    await _handle(message, state)


@router.message(F.chat.type == ChatType.PRIVATE, F.text & ~F.text.startswith("/"))
async def on_private_text(message: Message, state: FSMContext) -> None:
    await _handle(message, state)


async def _handle(message: Message, state: FSMContext) -> None:
    trigger = NewTaskTrigger()
    trigger_data = await trigger.run(message, state)
    code = NewTaskCode()
    code_result = await code.run(trigger_data, state)
    answer = _ANSWER_REGISTRY[code_result["answer_name"]]
    await answer.run(event=message, user_lang="ru", data=code_result["data"])
