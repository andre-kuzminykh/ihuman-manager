"""
Виджет: /setup_chat — подписка группового чата.

## Трассируемость
Feature: F005
Scenarios: SC011
"""

from __future__ import annotations

from aiogram import Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message

from node.chat.answer.chat_subscribed_answer import ChatSubscribedAnswer
from node.chat.code.chat_subscribe_code import ChatSubscribeCode


router = Router(name="chat.F005.setup")


@router.message(Command("setup_chat"))
async def on_setup_chat(message: Message) -> None:
    if message.chat.type == ChatType.PRIVATE:
        await message.answer("Команда работает только в групповом чате/канале.")
        return
    code = ChatSubscribeCode()
    result = await code.run(message)
    answer = ChatSubscribedAnswer()
    await answer.run(event=message, user_lang="ru", data=result.get("data", {}))
