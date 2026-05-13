"""
Виджет: /digest и /evening — дайджесты без кнопок.

## Трассируемость
Feature: F007, F011
Scenarios: SC018, SC019, SC028
"""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

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


@router.message(Command("evening"))
async def on_evening(message: Message) -> None:
    if message.from_user is None:
        return
    from service.api.digest_api import DigestAPI

    digest = await DigestAPI().evening_for_user(message.from_user.id)
    await DigestAnswer().run(
        event=message, user_lang="ru", data={"digest": digest, "evening": True}
    )
