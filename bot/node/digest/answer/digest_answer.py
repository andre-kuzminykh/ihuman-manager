"""
DigestAnswer — утренний дайджест.

## Трассируемость
Feature: F007
Scenarios: SC018, SC019
"""

from __future__ import annotations

from datetime import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from callback.digest_callback import DigestActionCallback
from core import vocab
from core.loader import get_bot


def _fmt(value: str | None) -> str:
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value).strftime("%H:%M")
    except ValueError:
        return value


def render_digest(digest: dict) -> str:
    if digest.get("is_empty"):
        return f"{vocab.MORNING_DIGEST_TITLE}\n\n{vocab.NO_TASKS_TODAY}"
    lines = [vocab.MORNING_DIGEST_TITLE, ""]
    for group in digest.get("groups", []):
        lines.append(f"<b>{group['label']}</b>")
        for t in group.get("tasks", []):
            fav = "⭐ " if t.get("is_favorite") else ""
            ps = _fmt(t.get("planned_start_at"))
            ps_label = f"({ps}) " if ps else ""
            lines.append(f"• {fav}{ps_label}{t['title']}")
        lines.append("")
    return "\n".join(lines).rstrip()


def build_digest_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🟢 Начать день",
                    callback_data=DigestActionCallback(action="start_day").pack(),
                ),
                InlineKeyboardButton(
                    text="🔄 Обновить",
                    callback_data=DigestActionCallback(action="refresh").pack(),
                ),
            ]
        ]
    )


class DigestAnswer:
    async def send(self, *, owner_chat_id: int, digest: dict) -> None:
        bot = get_bot()
        await bot.send_message(
            owner_chat_id, render_digest(digest), reply_markup=build_digest_kb()
        )

    async def run(self, *, event: Message, user_lang: str = "ru", data: dict) -> None:
        await event.answer(render_digest(data["digest"]), reply_markup=build_digest_kb())
