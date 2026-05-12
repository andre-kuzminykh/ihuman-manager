"""
TaskCreatedAnswer — карточка созданной задачи.

## Трассируемость
Feature: F001, F002, F003, F004
Scenarios: SC001, SC004, SC006, SC009
"""

from __future__ import annotations

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
    rows: list[list[InlineKeyboardButton]] = []
    status = task.get("status")
    tid = task["id"]
    if status in {"backlog", "todo"}:
        rows.append([
            InlineKeyboardButton(
                text="▶️ Начать",
                callback_data=TaskActionCallback(task_id=tid, action="start").pack(),
            )
        ])
    if status in {"todo", "in_progress"}:
        rows.append([
            InlineKeyboardButton(
                text="⏸ Пауза",
                callback_data=TaskActionCallback(task_id=tid, action="pause").pack(),
            ),
            InlineKeyboardButton(
                text="🛑 Заблок.",
                callback_data=TaskActionCallback(task_id=tid, action="block").pack(),
            ),
            InlineKeyboardButton(
                text="✅ Готово",
                callback_data=TaskActionCallback(task_id=tid, action="done").pack(),
            ),
        ])
    if status in {"paused", "blocked"}:
        rows.append([
            InlineKeyboardButton(
                text="▶️ Продолжить",
                callback_data=TaskActionCallback(task_id=tid, action="start").pack(),
            ),
            InlineKeyboardButton(
                text="✅ Готово",
                callback_data=TaskActionCallback(task_id=tid, action="done").pack(),
            ),
        ])
    fav_text = "⭐ Убрать" if task.get("is_favorite") else "⭐ В избранное"
    fav_action = "unfavorite" if task.get("is_favorite") else "favorite"
    rows.append([
        InlineKeyboardButton(
            text=fav_text,
            callback_data=TaskActionCallback(task_id=tid, action=fav_action).pack(),
        ),
        InlineKeyboardButton(
            text="🚫 Отменить",
            callback_data=TaskActionCallback(task_id=tid, action="cancel").pack(),
        ),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def render_task_card(task: dict, *, title_prefix: str = vocab.TASK_CREATED) -> str:
    fav_mark = "⭐ " if task.get("is_favorite") else ""
    return (
        f"{title_prefix}\n\n"
        f"{fav_mark}<b>{task.get('title','')}</b>\n"
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
