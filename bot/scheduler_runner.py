"""
scheduler_runner — фоновая корутина: каждые N секунд дёргает /scheduler/tick
и рассылает уведомления о дедлайнах и утренний дайджест.

## Трассируемость
Feature: F003 (SC007), F006 (SC015, SC017), F007 (SC018, SC019)
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from callback.tasks_callback import TaskActionCallback
from core import vocab
from core.loader import get_bot
from service.api.scheduler_api import SchedulerAPI


log = logging.getLogger("scheduler_runner")


def _build_deadline_kb(task_id: int) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text="⏸ Пауза",
                callback_data=TaskActionCallback(task_id=task_id, action="pause").pack(),
            ),
            InlineKeyboardButton(
                text="✅ Завершить",
                callback_data=TaskActionCallback(task_id=task_id, action="done").pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="📅 +1 день",
                callback_data=TaskActionCallback(
                    task_id=task_id, action="set_deadline_tomorrow"
                ).pack(),
            ),
            InlineKeyboardButton(
                text="🚫 Отмена",
                callback_data=TaskActionCallback(task_id=task_id, action="cancel").pack(),
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _send_deadline(item: dict[str, Any]) -> None:
    bot = get_bot()
    text = (
        f"{vocab.DEADLINE_NOTICE_TITLE}\n\n"
        f"Задача «{item.get('title','')}» уже на дедлайне.\n"
        f"Что делаем?"
    )
    await bot.send_message(
        item["user_id"], text, reply_markup=_build_deadline_kb(item["task_id"])
    )


async def _send_digest(item: dict[str, Any]) -> None:
    from node.digest.answer.digest_answer import DigestAnswer

    await DigestAnswer().send(owner_chat_id=item["user_id"], digest=item["digest"])


async def run_scheduler_loop(interval_seconds: int) -> None:
    api = SchedulerAPI()
    log.info("Scheduler loop started, interval=%s sec", interval_seconds)
    while True:
        try:
            result = await api.tick()
            for n in result.get("deadline_notifications", []):
                try:
                    await _send_deadline(n)
                except Exception:
                    log.exception("send deadline failed")
            for d in result.get("morning_digests", []):
                try:
                    await _send_digest(d)
                except Exception:
                    log.exception("send digest failed")
        except Exception:
            log.exception("scheduler tick failed")
        await asyncio.sleep(interval_seconds)
