"""
DirectionsListAnswer.

## Трассируемость
Feature: F009
Scenarios: SC022, SC023
"""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from callback.directions_callback import DirectionActionCallback


class DirectionsListAnswer:
    async def run(self, *, event: Message, user_lang: str = "ru", data: dict) -> None:
        items: list[dict] = data["directions"]
        if not items:
            await event.answer(
                "Направлений нет. Создай через /direction <название>."
            )
            return
        rows = []
        for d in items:
            mark = "⭐" if d.get("is_favorite") else "•"
            action = "unfavorite" if d.get("is_favorite") else "favorite"
            rows.append([
                InlineKeyboardButton(
                    text=f"{mark} {d['name']}",
                    callback_data=DirectionActionCallback(direction_id=d["id"], action=action).pack(),
                ),
                InlineKeyboardButton(
                    text="🗑",
                    callback_data=DirectionActionCallback(direction_id=d["id"], action="delete").pack(),
                ),
            ])
        await event.answer(
            "🧭 Направления:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
        )
