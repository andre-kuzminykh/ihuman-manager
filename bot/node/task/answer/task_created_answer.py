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
       строка 1: ▶️ Начать (большая) — если задача не активна
       строка 2: ⭐ Избранное (большая) — всегда
       строка 3: 🚫 Отменить · ✅ Готово · ⏸ Пауза (Пауза только когда in_progress)
    Для done/cancelled показываем только ↩️ Восстановить.
    """
    rows: list[list[InlineKeyboardButton]] = []
    status = task.get("status")
    tid = task["id"]

    if status in {"done", "cancelled"}:
        rows.append([
            InlineKeyboardButton(
                text="↩️ Вернуть в работу",
                callback_data=TaskActionCallback(task_id=tid, action="start").pack(),
            )
        ])
        return InlineKeyboardMarkup(inline_keyboard=rows)

    # большая «Начать / Продолжить»
    if status in {"backlog", "todo", "paused", "blocked"}:
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

    # нижний ряд
    bottom = [
        InlineKeyboardButton(
            text="🚫 Отменить",
            callback_data=TaskActionCallback(task_id=tid, action="cancel").pack(),
        ),
        InlineKeyboardButton(
            text="✅ Готово",
            callback_data=TaskActionCallback(task_id=tid, action="done").pack(),
        ),
    ]
    if status == "in_progress":
        bottom.append(
            InlineKeyboardButton(
                text="⏸ Пауза",
                callback_data=TaskActionCallback(task_id=tid, action="pause").pack(),
            )
        )
    rows.append(bottom)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def render_task_card(task: dict, *, title_prefix: str = vocab.TASK_CREATED) -> str:
    fav_mark = "⭐ " if task.get("is_favorite") else ""
    safe_title = html.escape(task.get("title", ""))
    return (
        f"{title_prefix}\n\n"
        f"{fav_mark}<b>{safe_title}</b>\n"
        f"Статус: {vocab.status_label(task.get('status',''))}\n"
        f"Дедлайн: {_fmt_deadline(task.get('deadline'))}\n"
        f"План: {_fmt_deadline(task.get('planned_start_at'))} — "
        f"{_fmt_deadline(task.get('planned_end_at'))}"
    )


class TaskCreatedAnswer:
    async def run(self, *, event: Message, user_lang: str = "ru", data: dict) -> None:
        task = data["task"]
        text = render_task_card(task)
        await event.answer(text, reply_markup=build_task_card_kb(task))
