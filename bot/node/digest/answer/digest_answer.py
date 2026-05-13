"""
DigestAnswer — утренний/вечерний дайджест.

## Трассируемость
Feature: F007, F011
Scenarios: SC018, SC019, SC028

Без кнопок: просто чистый список задач.
"""

from __future__ import annotations

import html
from datetime import datetime

from aiogram.types import Message

from core import vocab
from core.loader import get_bot


def _fmt(value: str | None) -> str:
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value).strftime("%H:%M")
    except ValueError:
        return value


def render_digest(digest: dict, *, evening: bool = False) -> str:
    title = vocab.EVENING_DIGEST_TITLE if evening else vocab.MORNING_DIGEST_TITLE
    if digest.get("is_empty"):
        return f"{title}\n\n{vocab.NO_TASKS_TODAY}"
    lines = [title, ""]
    for group in digest.get("groups", []):
        lines.append(f"<b>{html.escape(group['label'])}</b>")
        for t in group.get("tasks", []):
            fav = "⭐ " if t.get("is_favorite") else ""
            ps = _fmt(t.get("planned_start_at"))
            ps_label = f"({ps}) " if ps else ""
            lines.append(f"• {fav}{ps_label}{html.escape(t['title'])}")
        lines.append("")
    return "\n".join(lines).rstrip()


class DigestAnswer:
    async def send(
        self, *, owner_chat_id: int, digest: dict, evening: bool = False
    ) -> None:
        bot = get_bot()
        await bot.send_message(owner_chat_id, render_digest(digest, evening=evening))

    async def run(self, *, event: Message, user_lang: str = "ru", data: dict) -> None:
        await event.answer(
            render_digest(data["digest"], evening=data.get("evening", False)),
        )
