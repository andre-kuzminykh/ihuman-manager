"""
Тест SC012 — сообщение → PendingTask на согласование.

## Трассируемость
Feature: F005
Scenario: SC012
"""

from datetime import datetime, timezone

import pytest


@pytest.mark.asyncio
async def test_message_creates_pending(client, classify_as_task):
    await client.post(
        "/api/v1/chats/subscribe",
        json={"chat_id": -1002, "owner_user_id": 42},
    )
    response = await client.post(
        "/api/v1/messages/ingest",
        json={
            "chat_id": -1002,
            "message_id": 1,
            "sender_user_id": 7,
            "sender_username": "alex",
            "text": "Надо собрать отчёт к пятнице",
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "is_bot_mentioned": False,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "pending_created"
    assert body["pending_task_id"] is not None
