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
        user = message.from_user
        full = " ".join(filter(None, [
            getattr(user, "first_name", None), getattr(user, "last_name", None)
        ])).strip() if user else ""
        sender_display = full or (
            f"@{user.username}" if user and getattr(user, "username", None) else None
        )
        return {
            "user_id": user.id if user else 0,
            "text": payload,
            "source_kind": "text",
            "sender_user_id": user.id if user else None,
            "sender_username": getattr(user, "username", None) if user else None,
            "sender_display": sender_display,
        }
