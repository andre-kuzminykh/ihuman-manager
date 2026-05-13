"""
TaskCreatedAnswer — карточка созданной задачи.

## Трассируемость
Feature: F001, F002, F003, F004
Scenarios: SC001, SC004, SC006, SC009
"""

from __future__ import annotations

import html
from datetime import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from callback.tasks_callback import TaskActionCallback
from core import vocab


def _fmt_deadline(value: str | None) -> str:
    if not value:
        return "—"
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%d.%m.%Y %H:%M")
    except ValueError:
        return value


def build_task_card_kb(task: dict) -> InlineKeyboardMarkup:
    """Раскладка карточки:
       Row 1 (большая): Начать ↔ Пауза (тогл по статусу). Для done/cancelled — Вернуть.
       Row 2 (большая): ⭐ В избранное / ⭐ Убрать.
       Row 3 (две кнопки): 🚫 Отмена · ✅ Готово. Без Пауза в этом ряду.
    """
    rows: list[list[InlineKeyboardButton]] = []
    status = task.get("status")
    tid = task["id"]

    # Row 1 — большой главный экшен.
    if status == "in_progress":
        primary_text, primary_action = "⏸ Пауза", "pause"
    elif status in {"paused", "blocked"}:
        primary_text, primary_action = "▶️ Продолжить", "start"
    elif status in {"done", "cancelled"}:
        primary_text, primary_action = "↩️ Вернуть в работу", "reopen"
    else:
        primary_text, primary_action = "▶️ Начать", "start"
    rows.append([
        InlineKeyboardButton(
            text=primary_text,
            callback_data=TaskActionCallback(task_id=tid, action=primary_action).pack(),
        )
    ])

    # done/cancelled — больше ничего не показываем.
    if status in {"done", "cancelled"}:
        return InlineKeyboardMarkup(inline_keyboard=rows)

    # Row 2 — большая «Избранное».
    fav_text = "⭐ Убрать из избранного" if task.get("is_favorite") else "⭐ В избранное"
    fav_action = "unfavorite" if task.get("is_favorite") else "favorite"
    rows.append([
        InlineKeyboardButton(
            text=fav_text,
            callback_data=TaskActionCallback(task_id=tid, action=fav_action).pack(),
        )
    ])

    # Row 3 — Отмена + Готово (без Пауза).
    rows.append([
        InlineKeyboardButton(
            text="🚫 Отмена",
            callback_data=TaskActionCallback(task_id=tid, action="cancel").pack(),
        ),
        InlineKeyboardButton(
            text="✅ Готово",
            callback_data=TaskActionCallback(task_id=tid, action="done").pack(),
        ),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


_PRIORITY_EMOJI = {"low": "🟢", "medium": "🟡", "high": "🔴"}


def _source_url(task: dict) -> str | None:
    chat_id = task.get("chat_id")
    msg_id = task.get("source_message_id")
    if not chat_id:
        return None
    cid = int(chat_id)
    # Supergroups / channels — публичная ссылка на конкретное сообщение.
    if cid < 0 and str(cid).startswith("-100") and msg_id:
        return f"https://t.me/c/{str(cid)[4:]}/{msg_id}"
    # Private DM / private group — нет URL на конкретное сообщение.
    # Фоллбек: t.me/<username> отправителя.
    sender = task.get("source_sender") or task.get("source_sender_username")
    if sender:
        return f"https://t.me/{sender}"
    return None


def render_task_card(task: dict, *, title_prefix: str | None = None) -> str:
    fav_mark = "⭐ " if task.get("is_favorite") else ""
    safe_title = html.escape(task.get("title", ""))
    prio = task.get("priority") or "medium"
    prio_emoji = _PRIORITY_EMOJI.get(prio, "🟡")
    src_url = _source_url(task)
    title_block = f"<b>{safe_title}</b>"
    if src_url:
        title_block = f'<a href="{src_url}"><b>{safe_title}</b></a>'

    lines = []
    if title_prefix:
        lines.extend([title_prefix, ""])
    lines.append(f"{prio_emoji} {fav_mark}{title_block}")

    desc = task.get("description")
    if desc:
        lines.append(f"📝 {html.escape(desc)}")

    deadline = task.get("deadline")
    if deadline:
        try:
            dt = datetime.fromisoformat(deadline)
            lines.append(f"📅 {dt.strftime('%Y-%m-%d · %H:%M')}")
        except (ValueError, TypeError):
            lines.append(f"📅 {deadline}")

    ps = task.get("planned_start_at")
    pe = task.get("planned_end_at")
    if ps or pe:
        lines.append(f"⏱ План: {_fmt_deadline(ps)} — {_fmt_deadline(pe)}")

    status = task.get("status")
    if status and status not in {"todo"}:
        lines.append(f"Статус: {vocab.status_label(status)}")

    return "\n".join(lines)


class TaskCreatedAnswer:
    async def run(self, *, event: Message, user_lang: str = "ru", data: dict) -> None:
        task = data["task"]
        # Никаких лишних префиксов — сразу карточка задачи.
        text = render_task_card(task)
        await event.answer(
            text, reply_markup=build_task_card_kb(task), disable_web_page_preview=True
        )
