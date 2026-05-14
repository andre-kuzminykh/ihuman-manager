"""
Тест SC014b — одно сообщение с двумя задачами → два PendingTask.

## Трассируемость
Feature: F005
Scenario: SC014b
"""

from datetime import datetime, timezone

import pytest

from service.extractor.extractor_service import ExtractorService


@pytest.mark.asyncio
async def test_multi_pendings_created(client, monkeypatch):
    async def fake_extract(self, text, *, context_messages=None, sender_display=None):
        return [
            {
                "title": "Купить молоко",
                "description": "Нужно купить молоко завтра утром",
                "text": "купить молоко",
                "deadline": None,
                "priority": "medium",
                "confidence": 0.9,
            },
            {
                "title": "Подготовить презентацию",
                "description": "Презентация партнёрам по AI-трансформации бизнеса",
                "text": "подготовить презу",
                "deadline": None,
                "priority": "high",
                "confidence": 0.9,
            },
        ]

    monkeypatch.setattr(ExtractorService, "extract_multiple", fake_extract)

    # подписать чат
    await client.post(
        "/api/v1/chats/subscribe",
        json={"chat_id": -2002, "owner_user_id": 7},
    )
    resp = await client.post(
        "/api/v1/messages/ingest",
        json={
            "chat_id": -2002,
            "message_id": 1,
            "sender_user_id": 7,
            "sender_username": "andrey",
            "text": "купить молоко и сделать презентацию для партнеров",
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "is_bot_mentioned": False,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["decision"] == "pending_created_multi"
    assert len(body["pending_task_ids"]) == 2

    # каждая Pending имеет свои draft-поля
    pending_a = await client.get(f"/api/v1/pending-tasks/{body['pending_task_ids'][0]}")
    pending_b = await client.get(f"/api/v1/pending-tasks/{body['pending_task_ids'][1]}")
    assert pending_a.status_code == 200 and pending_b.status_code == 200
    draft_a = pending_a.json()["draft"]
    draft_b = pending_b.json()["draft"]
    titles = {draft_a["title"], draft_b["title"]}
    assert {"Купить молоко", "Подготовить презентацию"} == titles
    # description у каждой свой
    descs = {draft_a.get("description"), draft_b.get("description")}
    assert "Нужно купить молоко завтра утром" in descs
    # priority различается — у второй "high"
    prios = {draft_a.get("priority"), draft_b.get("priority")}
    assert "high" in prios and "medium" in prios
