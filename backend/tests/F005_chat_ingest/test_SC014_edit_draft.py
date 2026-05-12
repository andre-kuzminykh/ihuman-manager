"""
Тест SC014 — редактирование draft перед апрувом.

## Трассируемость
Feature: F005
Scenario: SC014
"""

from datetime import datetime, timezone

import pytest


@pytest.mark.asyncio
async def test_edit_pending_then_approve(client, classify_as_task):
    await client.post(
        "/api/v1/chats/subscribe", json={"chat_id": -1004, "owner_user_id": 42}
    )
    response = await client.post(
        "/api/v1/messages/ingest",
        json={
            "chat_id": -1004,
            "message_id": 20,
            "sender_username": "alex",
            "text": "собрать отчёт",
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "is_bot_mentioned": False,
        },
    )
    pending_id = response.json()["pending_task_id"]

    response = await client.put(
        f"/api/v1/pending-tasks/{pending_id}",
        json={
            "title": "Собрать квартальный отчёт",
            "deadline": "2026-05-20T18:00:00+03:00",
        },
    )
    assert response.status_code == 200
    assert response.json()["draft"]["title"] == "Собрать квартальный отчёт"

    response = await client.post(f"/api/v1/pending-tasks/{pending_id}/approve")
    assert response.status_code == 200
    body = response.json()
    assert body["approved"] is True
    assert body["created_task_id"] is not None
