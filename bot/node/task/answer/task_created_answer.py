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
       строка 1: ▶️ Начать (большая) — если задача в backlog/todo/paused/blocked
       строка 2: ⭐ Избранное (большая) — всегда
       строка 3: 🚫 Отменить · ⏸ Пауза · ✅ Готово (Пауза только когда in_progress)
    Для done/cancelled — ↩️ Вернуть в работу (через action='reopen' → status=todo).
    """
    rows: list[list[InlineKeyboardButton]] = []
    status = task.get("status")
    tid = task["id"]

    if status in {"done", "cancelled"}:
        rows.append([
            InlineKeyboardButton(
                text="↩️ Вернуть в работу",
                callback_data=TaskActionCallback(task_id=tid, action="reopen").pack(),
            )
        ])
        return InlineKeyboardMarkup(inline_keyboard=rows)

    # большая «Начать / Продолжить»
    start_label = "▶️ Продолжить" if status in {"paused", "blocked"} else "▶️ Начать"
    rows.append([
        InlineKeyboardButton(
            text=start_label,
            callback_data=TaskActionCallback(task_id=tid, action="start").pack(),
        )
    ])

    # большая «Избранное»
    fav_text = "⭐ Убрать из избранного" if task.get("is_favorite") else "⭐ В избранное"
    fav_action = "unfavorite" if task.get("is_favorite") else "favorite"
    rows.append([
        InlineKeyboardButton(
            text=fav_text,
            callback_data=TaskActionCallback(task_id=tid, action=fav_action).pack(),
        )
    ])

    # нижний ряд: Отменить → Пауза (только in_progress) → Готово
    bottom = [
        InlineKeyboardButton(
            text="🚫 Отменить",
            callback_data=TaskActionCallback(task_id=tid, action="cancel").pack(),
        )
    ]
    if status == "in_progress":
        bottom.append(
            InlineKeyboardButton(
                text="⏸ Пауза",
                callback_data=TaskActionCallback(task_id=tid, action="pause").pack(),
            )
        )
    bottom.append(
        InlineKeyboardButton(
            text="✅ Готово",
            callback_data=TaskActionCallback(task_id=tid, action="done").pack(),
        )
    )
    rows.append(bottom)
    return InlineKeyboardMarkup(inline_keyboard=rows)


_PRIORITY_EMOJI = {"low": "🟢", "medium": "🟡", "high": "🔴"}


def _source_url(task: dict) -> str | None:
    chat_id = task.get("chat_id")
    msg_id = task.get("source_message_id")
    if not chat_id or not msg_id:
        return None
    # Supergroups / channels: chat_id вида -100xxxxxxxxxx → t.me/c/xxxxxxxxxx/<msg>
    # Обычные private groups (chat_id < 0 без -100) — нет публичной ссылки.
    cid = int(chat_id)
    if cid < 0 and str(cid).startswith("-100"):
        public_id = str(cid)[4:]  # отрезаем "-100"
        return f"https://t.me/c/{public_id}/{msg_id}"
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
        prefix = vocab.TASK_CREATED if not data.get("from_pending") else "✅ Задача создана из согласования"
        text = render_task_card(task, title_prefix=prefix)
        await event.answer(
            text, reply_markup=build_task_card_kb(task), disable_web_page_preview=True
        )
