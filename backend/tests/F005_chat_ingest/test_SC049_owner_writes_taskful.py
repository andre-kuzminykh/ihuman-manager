"""
SC049 — сообщение от самого владельца в подписанном чате тоже становится
задачей. Автор владельца **сохраняется** в pending/task (а не обнуляется,
как было раньше), чтобы на карточке 👤-строка не пропадала.

## Трассируемость
Feature: F005
Scenario: SC049 — owner-writes-to-others с сохранением автора.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from service.extractor.extractor_service import ExtractorService


@pytest.mark.asyncio
async def test_owner_message_creates_pending_without_author(client, monkeypatch):
    captured_sender_display: list[str | None] = []

    async def fake_extract(self, text, *, context_messages=None, sender_display=None):
        captured_sender_display.append(sender_display)
        return [
            {
                "title": "Подготовить отчёт",
                "description": None,
                "text": "Подготовить отчёт до пятницы",
                "deadline": None,
                "priority": "medium",
                "confidence": 0.9,
            }
        ]

    monkeypatch.setattr(ExtractorService, "extract_multiple", fake_extract)

    # 1) подписываем чат на этого же владельца
    owner_user_id = 42
    await client.post(
        "/api/v1/chats/subscribe",
        json={"chat_id": -3003, "owner_user_id": owner_user_id},
    )

    # 2) ingest — владелец пишет сам себе/команде в подписанном чате
    resp = await client.post(
        "/api/v1/messages/ingest",
        json={
            "chat_id": -3003,
            "message_id": 1,
            "sender_user_id": owner_user_id,
            "sender_username": "owner",
            "sender_first_name": "Owner",
            "sender_last_name": "",
            "text": "Подготовить отчёт до пятницы",
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "is_bot_mentioned": False,
            "chat_username": None,
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["decision"] == "pending_created", body

    # decomposer вызван и получил реального автора (Owner) — даже для self-write
    assert captured_sender_display, "extractor must be invoked for self-write"
    assert captured_sender_display[0] == "Owner"

    # Pending с заполненным автором — на карточке появится 👤
    pending_id = body["pending_task_id"]
    p = await client.get(f"/api/v1/pending-tasks/{pending_id}")
    assert p.status_code == 200
    p_body = p.json()
    assert p_body.get("source_sender_display") == "Owner"
    assert p_body.get("source_sender_user_id") == owner_user_id
