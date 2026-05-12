"""
Тест SC011 — подписка чата.

## Трассируемость
Feature: F005
Scenario: SC011
"""

import pytest


@pytest.mark.asyncio
async def test_subscribe_chat(client):
    response = await client.post(
        "/api/v1/chats/subscribe",
        json={"chat_id": -1001, "owner_user_id": 42, "title": "Team"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["chat_id"] == -1001
    assert body["enabled"] is True
