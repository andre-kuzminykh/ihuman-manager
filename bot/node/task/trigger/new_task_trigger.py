"""
NewTaskTrigger — извлекает аргумент из /new ... и сбрасывает FSM.

## Трассируемость
Feature: F001
Scenarios: SC001, SC002, SC003
"""

from __future__ import annotations

from aiogram.fsm.context import FSMContext
from aiogram.types import Message


class NewTaskTrigger:
    async def run(self, message: Message, state: FSMContext) -> dict:
        await state.clear()
        raw = message.text or ""
        # /new <text> либо просто текст
        if raw.startswith("/new"):
            payload = raw[len("/new"):].strip()
        else:
            payload = raw.strip()
        return {
            "user_id": message.from_user.id if message.from_user else 0,
            "text": payload,
            "source_kind": "text",
        }
