"""
PendingCardAnswer — карточка задачи на согласование.

## Трассируемость
Feature: F005
Scenarios: SC012, SC014
"""

from __future__ import annotations

import html
from datetime import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from callback.pending_callback import PendingActionCallback
from core import vocab
from core.loader import get_bot


def _fmt(value: str | None) -> str:
    if not value:
        return "—"
    try:
        return datetime.fromisoformat(value).strftime("%d.%m.%Y %H:%M")
    except ValueError:
        return value


def render_pending_text(pending: dict) -> str:
    draft = pending.get("draft") or {}
    title = draft.get("title") or pending.get("source_text", "")[:80]
    deadline = _fmt(draft.get("deadline"))
    sender = pending.get("source_sender") or "—"
    return (
        f"{vocab.PENDING_CARD_TITLE}\n\n"
        f"<b>{html.escape(title)}</b>\n"
        f"Дедлайн: {deadline}\n"
        f"Из чата: {pending.get('chat_id')} (от {html.escape(str(sender))})\n"
        f"Исходный текст: <i>{html.escape(pending.get('source_text',''))}</i>"
    )


def build_pending_kb(pending_id: int) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text="✅ Принять",
                callback_data=PendingActionCallback(pending_id=pending_id, action="approve").pack(),
            ),
            InlineKeyboardButton(
                text="🚫 Отклонить",
                callback_data=PendingActionCallback(pending_id=pending_id, action="reject").pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="✏️ Заголовок",
                callback_data=PendingActionCallback(pending_id=pending_id, action="edit_title").pack(),
            ),
            InlineKeyboardButton(
                text="📅 Дедлайн",
                callback_data=PendingActionCallback(pending_id=pending_id, action="edit_deadline").pack(),
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


class PendingCardAnswer:
    async def send(self, *, owner_chat_id: int, pending: dict) -> None:
        bot = get_bot()
        await bot.send_message(
            owner_chat_id,
            render_pending_text(pending),
            reply_markup=build_pending_kb(pending["id"]),
        )

    async def run(self, *, event, user_lang: str = "ru", data: dict) -> None:
        pending = data["pending"]
        await event.answer(
            render_pending_text(pending),
            reply_markup=build_pending_kb(pending["id"]),
        )
