"""
Тест SC013 — тег бота в чате → автоапрув + создание задачи.

## Трассируемость
Feature: F005
Scenario: SC013
"""

from datetime import datetime, timezone

import pytest


@pytest.mark.asyncio
async def test_bot_mention_auto_approves(client, classify_as_task):
    await client.post(
        "/api/v1/chats/subscribe", json={"chat_id": -1003, "owner_user_id": 42}
    )
    response = await client.post(
        "/api/v1/messages/ingest",
        json={
            "chat_id": -1003,
            "message_id": 10,
            "sender_username": "alex",
            "text": "@hmnd_taskbot Подготовить презентацию до пятницы",
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "is_bot_mentioned": True,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "auto_approved"
    assert body["task_id"] is not None
