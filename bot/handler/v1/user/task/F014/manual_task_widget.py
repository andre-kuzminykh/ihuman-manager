"""
Виджет: ручная команда /task <title> [| <deadline>] [| <direction>].

## Трассируемость
Feature: F014
Scenarios: SC032

## Бизнес-правила
- Разделитель — '|' (BR039).
- deadline: ISO 8601 или относительный текст ('tomorrow 18:00') — парсится бэкендом.
- direction: имя существующего; если не найдено — пропускается с предупреждением.
- Дедуп пропускается (force=True): ручная команда — явное намерение.
"""

from __future__ import annotations

from datetime import datetime

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from core import vocab
from node.task.answer.task_created_answer import TaskCreatedAnswer
from node.task.answer.task_empty_error_answer import TaskEmptyErrorAnswer
from service.api.base_api import APIError
from service.api.directions_api import DirectionsAPI
from service.api.tasks_api import TasksAPI


router = Router(name="task.F014.manual")


def _parse_args(args: str) -> tuple[str, str | None, str | None]:
    parts = [p.strip() for p in args.split("|")]
    title = parts[0] if parts else ""
    deadline = parts[1] if len(parts) > 1 and parts[1] else None
    direction = parts[2] if len(parts) > 2 and parts[2] else None
    return title, deadline, direction


def _try_parse_deadline(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


@router.message(Command("task"))
async def on_manual_task(message: Message, command: CommandObject) -> None:
    if message.from_user is None:
        return
    args = (command.args or "").strip()
    if not args:
        await message.answer(
            "Использование: /task &lt;title&gt; | &lt;ISO deadline&gt; | &lt;direction&gt;"
        )
        return
    title, deadline_raw, direction_name = _parse_args(args)
    if not title:
        await TaskEmptyErrorAnswer().run(event=message, user_lang="ru", data={})
        return

    deadline = _try_parse_deadline(deadline_raw) if deadline_raw else None

    direction_id: int | None = None
    warning = None
    if direction_name:
        directions = await DirectionsAPI().list(user_id=message.from_user.id)
        found = next(
            (d for d in directions if d["name"].lower() == direction_name.lower()),
            None,
        )
        if found:
            direction_id = found["id"]
        else:
            warning = (
                f"⚠️ Направление '{direction_name}' не найдено — задача создана без него."
            )

    user = message.from_user
    full = " ".join(filter(None, [user.first_name, user.last_name])).strip() if user else ""
    sender_display = full or (
        f"@{user.username}" if user and user.username else None
    )
    api = TasksAPI()
    try:
        task = await api.create(
            user_id=user.id,
            text=title,
            title=title,
            deadline=deadline,
            direction_id=direction_id,
            force=True,  # BR031 — ручной ввод пропускает дедуп
            source_kind="manual",
            source_sender_user_id=user.id if user else None,
            source_sender_username=user.username if user else None,
            source_sender_display=sender_display,
        )
    except APIError as exc:
        await message.answer(f"❌ {exc.message}")
        return

    if warning:
        await message.answer(warning)
    await TaskCreatedAnswer().run(event=message, user_lang="ru", data={"task": task})
