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


_PRIORITY_EMOJI = {"low": "🟢", "medium": "🟡", "high": "🔴"}


def _fmt(value: str | None) -> str:
    if not value:
        return "—"
    try:
        return datetime.fromisoformat(value).strftime("%Y-%m-%d · %H:%M")
    except ValueError:
        return value


def _source_url(pending: dict) -> str | None:
    chat_id = pending.get("chat_id")
    msg_id = pending.get("message_id")
    if not chat_id or not msg_id:
        return None
    cid = int(chat_id)
    if cid < 0 and str(cid).startswith("-100"):
        return f"https://t.me/c/{str(cid)[4:]}/{msg_id}"
    return None


def render_pending_text(pending: dict) -> str:
    draft = pending.get("draft") or {}
    title = (draft.get("title") or pending.get("source_text", "")[:80]).strip()
    desc = draft.get("description") or pending.get("source_text", "")
    deadline = draft.get("deadline")
    prio = (draft.get("priority") or "medium").lower()
    prio_emoji = _PRIORITY_EMOJI.get(prio, "🟡")

    title_block = f"<b>{html.escape(title)}</b>"
    src_url = _source_url(pending)
    if src_url:
        title_block = f'<a href="{src_url}"><b>{html.escape(title)}</b></a>'

    lines = [
        f"{vocab.PENDING_CARD_TITLE} #{pending.get('id')}",
        "",
        f"{prio_emoji} {title_block}",
    ]
    if desc:
        lines.append(f"📝 {html.escape(desc)}")
    if deadline:
        lines.append(f"📅 {_fmt(deadline)}")

    sender = pending.get("source_sender") or "—"
    lines.append(f"<i>Из чата · от {html.escape(str(sender))}</i>")
    return "\n".join(lines)


def build_pending_kb(pending_id: int) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text="🚫 Reject",
                callback_data=PendingActionCallback(pending_id=pending_id, action="reject").pack(),
            ),
            InlineKeyboardButton(
                text="✏️ Edit",
                callback_data=PendingActionCallback(pending_id=pending_id, action="edit").pack(),
            ),
            InlineKeyboardButton(
                text="✅ Accept",
                callback_data=PendingActionCallback(pending_id=pending_id, action="approve").pack(),
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
