"""
ChatSubscribeCode.

## Трассируемость
Feature: F005
Scenarios: SC011
"""

from __future__ import annotations

from aiogram.types import Message

from service.api.base_api import APIError
from service.api.chats_api import ChatsAPI


class ChatSubscribeCode:
    def __init__(self, api: ChatsAPI | None = None) -> None:
        self._api = api or ChatsAPI()

    async def run(self, message: Message) -> dict:
        if message.from_user is None or message.chat is None:
            return {"answer_name": "chat_subscribe_error", "data": {"message": "bad payload"}}
        try:
            sub = await self._api.subscribe(
                chat_id=message.chat.id,
                owner_user_id=message.from_user.id,
                title=message.chat.title,
            )
        except APIError as exc:
            return {"answer_name": "chat_subscribe_error", "data": {"message": exc.message}}
        return {"answer_name": "chat_subscribed", "data": {"subscription": sub}}
