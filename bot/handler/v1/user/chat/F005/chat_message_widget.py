"""
Виджет: ловим сообщения в групповых чатах и каналах → /messages/ingest.

## Трассируемость
Feature: F005
Scenarios: SC012, SC013
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.types import Message

from node.chat.code.chat_message_code import ChatMessageCode
from node.pending.answer.pending_card_answer import PendingCardAnswer
from node.task.answer.task_created_answer import build_task_card_kb, render_task_card
from core.loader import get_bot
from service.api.base_api import APIError
from service.api.people_api import PeopleAPI


router = Router(name="chat.F005.message")


@router.channel_post(F.text | F.caption)
@router.message(
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
    F.text | F.caption,
)
async def on_chat_message(message: Message) -> None:
    if message.from_user is not None and message.from_user.is_bot:
        return
    # touch People — фиксируем кто пишет.
    if message.from_user is not None:
        try:
            await PeopleAPI().touch(
                telegram_user_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                is_bot=message.from_user.is_bot,
                language_code=getattr(message.from_user, "language_code", None),
                is_premium=bool(getattr(message.from_user, "is_premium", False)),
            )
        except APIError:
            pass
    code = ChatMessageCode()
    result = await code.run(message)
    decision = result["answer_name"]

    if decision == "pending_card_dm":
        pending = result["data"]["pending"]
        await PendingCardAnswer().send(
            owner_chat_id=pending["owner_user_id"], pending=pending
        )
    elif decision == "pendings_multi_dm":
        pendings = result["data"]["pendings"]
        for p in pendings:
            await PendingCardAnswer().send(
                owner_chat_id=p["owner_user_id"], pending=p
            )
    elif decision == "task_created_dm":
        task = result["data"]["task"]
        bot = get_bot()
        await bot.send_message(
            task["user_id"],
            render_task_card(task),
            reply_markup=build_task_card_kb(task),
            disable_web_page_preview=True,
        )
    elif decision == "tasks_created_multi_dm":
        tasks = result["data"]["tasks"]
        if not tasks:
            return
        bot = get_bot()
        owner_id = tasks[0]["user_id"]
        for t in tasks:
            await bot.send_message(
                owner_id,
                render_task_card(t),
                reply_markup=build_task_card_kb(t),
                disable_web_page_preview=True,
            )
    # not_subscribed / ignored / duplicate — никаких сообщений в чат не шлём.
