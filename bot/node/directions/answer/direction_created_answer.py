"""
## Трассируемость
Feature: F009
Scenarios: SC022, SC024
"""

from __future__ import annotations

import html

from aiogram.types import Message


class DirectionCreatedAnswer:
    async def run(self, *, event: Message, user_lang: str = "ru", data: dict) -> None:
        direction = data.get("direction")
        if direction is None:
            await event.answer(data.get("message") or "Не удалось создать направление")
            return
        fav = " ⭐" if direction.get("is_favorite") else ""
        name_safe = html.escape(direction["name"])
        await event.answer(f"🧭 Направление создано: <b>{name_safe}</b>{fav}")
