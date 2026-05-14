"""
Тест SC040 — touch upsert.

## Трассируемость
Feature: F020
Scenario: SC040
"""

import pytest


@pytest.mark.asyncio
async def test_touch_creates_then_increments(client):
    body = {"telegram_user_id": 42, "username": "alice", "first_name": "Alice"}
    r1 = await client.post("/api/v1/people/touch", json=body)
    assert r1.status_code == 200
    p1 = r1.json()
    assert p1["telegram_user_id"] == 42
    assert p1["message_count"] == 1
    seen1 = p1["last_seen_at"]

    # повторный touch — должен инкрементить count и обновить last_seen_at
    r2 = await client.post("/api/v1/people/touch", json=body)
    p2 = r2.json()
    assert p2["id"] == p1["id"]
    assert p2["message_count"] == 2

    # список
    r3 = await client.get("/api/v1/people/")
    assert r3.status_code == 200
    items = r3.json()
    assert any(p["telegram_user_id"] == 42 for p in items)
