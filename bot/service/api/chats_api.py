"""
ChatsAPI.

## Трассируемость
Feature: F005
Scenarios: SC011, SC012, SC013
"""

from __future__ import annotations

from datetime import datetime

from service.api.base_api import BaseAPI


class ChatsAPI(BaseAPI):
    async def subscribe(
        self, *, chat_id: int, owner_user_id: int, title: str | None = None
    ) -> dict:
        return await self._request(
            "POST",
            "/chats/subscribe",
            json={"chat_id": chat_id, "owner_user_id": owner_user_id, "title": title},
        )

    async def unsubscribe(self, chat_id: int) -> None:
        await self._request("DELETE", f"/chats/subscribe/{chat_id}")

    async def ingest_message(
        self,
        *,
        chat_id: int,
        message_id: int,
        sender_user_id: int | None,
        sender_username: str | None,
        text: str,
        sent_at: datetime,
        is_bot_mentioned: bool,
    ) -> dict:
        return await self._request(
            "POST",
            "/messages/ingest",
            json={
                "chat_id": chat_id,
                "message_id": message_id,
                "sender_user_id": sender_user_id,
                "sender_username": sender_username,
                "text": text,
                "sent_at": sent_at.isoformat(),
                "is_bot_mentioned": is_bot_mentioned,
            },
        )
