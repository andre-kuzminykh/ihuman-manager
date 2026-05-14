"""
Виджет: команда /people — список контактов.

## Трассируемость
Feature: F020
Scenarios: SC041
"""

from __future__ import annotations

import html
from datetime import datetime, timedelta, timezone

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from service.api.people_api import PeopleAPI


router = Router(name="people.F020")
_MSK = timezone(timedelta(hours=3))


def _fmt_seen(value: str | None) -> str:
    if not value:
        return "—"
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(_MSK).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return value


@router.message(Command("people"))
async def on_people(message: Message) -> None:
    api = PeopleAPI()
    items = await api.list_all()
    if not items:
        await message.answer("Контактов ещё нет. Появятся после первых сообщений.")
        return
    lines = [f"👥 Контакты — {len(items)}", ""]
    for p in items[:50]:  # лимит для одного сообщения
        name = " ".join(filter(None, [p.get("first_name"), p.get("last_name")])) or "—"
        username = f"@{p['username']}" if p.get("username") else ""
        bot_mark = " 🤖" if p.get("is_bot") else ""
        premium = " ⭐" if p.get("is_premium") else ""
        seen = _fmt_seen(p.get("last_seen_at"))
        count = p.get("message_count") or 0
        line = (
            f"• <b>{html.escape(name)}</b>{bot_mark}{premium} "
            f"{html.escape(username)} — {count} сообщ., посл. {seen}"
        )
        lines.append(line)
    if len(items) > 50:
        lines.append("")
        lines.append(f"… и ещё {len(items) - 50}")
    await message.answer("\n".join(lines), disable_web_page_preview=True)
