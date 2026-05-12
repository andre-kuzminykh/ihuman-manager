"""
Виджет: /digest — дайджест на сегодня + кнопки.

## Трассируемость
Feature: F007
Scenarios: SC018, SC019
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from callback.digest_callback import DigestActionCallback
from node.digest.answer.digest_answer import DigestAnswer
from node.digest.code.digest_code import DigestCode


router = Router(name="digest.F007")


@router.message(Command("digest"))
async def on_digest(message: Message) -> None:
    if message.from_user is None:
        return
    code = DigestCode()
    result = await code.run(message.from_user.id)
    await DigestAnswer().run(event=message, user_lang="ru", data=result["data"])


@router.callback_query(DigestActionCallback.filter(F.action == "refresh"))
async def on_refresh(cb: CallbackQuery, callback_data: DigestActionCallback) -> None:
    if cb.from_user is None:
        await cb.answer()
        return
    code = DigestCode()
    result = await code.run(cb.from_user.id)
    if cb.message is not None:
        from node.digest.answer.digest_answer import build_digest_kb, render_digest

        await cb.message.edit_text(
            render_digest(result["data"]["digest"]), reply_markup=build_digest_kb()
        )
    await cb.answer("Обновлено")


@router.callback_query(DigestActionCallback.filter(F.action == "start_day"))
async def on_start_day(cb: CallbackQuery, callback_data: DigestActionCallback) -> None:
    await cb.answer("Хорошего дня! 💪", show_alert=True)
