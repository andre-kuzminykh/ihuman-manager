"""
TaskListAnswer — список задач сгруппированный по статусу.

## Трассируемость
Feature: F003, F004
Scenarios: SC006, SC009
"""

from __future__ import annotations

import html
from collections import defaultdict
from datetime import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from callback.tasks_callback import TaskCardCallback
from core import vocab


def _fmt(value: str | None) -> str:
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value).strftime("%d.%m %H:%M")
    except ValueError:
        return value


class TaskListAnswer:
    async def run(self, *, event: Message, user_lang: str = "ru", data: dict) -> None:
        tasks: list[dict] = data["tasks"]
        if not tasks:
            await event.answer("Задач нет. Создай через /new.")
            return
        groups: dict[str, list[dict]] = defaultdict(list)
        for t in tasks:
            groups[t["status"]].append(t)
        lines = []
        keyboard: list[list[InlineKeyboardButton]] = []
        order = ["in_progress", "todo", "backlog", "paused", "done", "cancelled"]
        for status in order:
            chunk = groups.get(status, [])
            if not chunk:
                continue
            lines.append(f"\n<b>{html.escape(vocab.status_label(status))}</b>")
            for t in chunk:
                fav = "⭐ " if t.get("is_favorite") else ""
                title_safe = html.escape(t["title"])
                lines.append(f"• {fav}{title_safe} ({_fmt(t.get('deadline'))})")
                keyboard.append([
                    InlineKeyboardButton(
                        text=f"{fav}{t['title'][:32]}",
                        callback_data=TaskCardCallback(task_id=t["id"], action="show").pack(),
                    )
                ])
        text = "📋 Задачи:" + "\n".join(lines)
        await event.answer(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard) if keyboard else None,
        )
