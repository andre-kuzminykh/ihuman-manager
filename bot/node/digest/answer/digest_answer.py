"""
DigestAnswer — утренний/вечерний дайджест.

## Трассируемость
Feature: F007, F011
Scenarios: SC018, SC019, SC028

Без кнопок: просто чистый список задач.
"""

from __future__ import annotations

import html
from datetime import datetime, timedelta, timezone

from aiogram.types import Message

from core import vocab
from core.loader import get_bot


_MSK = timezone(timedelta(hours=3))


def _to_msk(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc).astimezone(_MSK)
    return dt.astimezone(_MSK)


def _fmt(value: str | None) -> str:
    if not value:
        return ""
    try:
        return _to_msk(datetime.fromisoformat(value)).strftime("%H:%M")
    except ValueError:
        return value


def render_digest(digest: dict, *, evening: bool = False) -> str:
    title = vocab.EVENING_DIGEST_TITLE if evening else vocab.MORNING_DIGEST_TITLE
    subtitle = vocab.EVENING_DIGEST_SUBTITLE if evening else vocab.MORNING_DIGEST_SUBTITLE
    if digest.get("is_empty"):
        return f"{title}\n\n{vocab.NO_TASKS_TODAY}"

    # Плоский список без status-групп: избранные впереди, потом по дедлайну.
    # Между задачами оставляем пустую строку для воздуха.
    all_tasks: list[dict] = []
    for group in digest.get("groups", []):
        all_tasks.extend(group.get("tasks", []))
    all_tasks.sort(
        key=lambda t: (
            0 if t.get("is_favorite") else 1,
            t.get("planned_start_at") or t.get("deadline") or "",
            t.get("id", 0),
        )
    )

    parts = [title, "", subtitle, ""]
    for t in all_tasks:
        fav = "⭐ " if t.get("is_favorite") else ""
        ps = _fmt(t.get("planned_start_at"))
        ps_label = f"({ps}) " if ps else ""
        parts.append(f"• {fav}{ps_label}{html.escape(t['title'])}")
        parts.append("")
    return "\n".join(parts).rstrip()


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
