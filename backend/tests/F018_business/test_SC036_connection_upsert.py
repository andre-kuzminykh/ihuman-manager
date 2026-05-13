"""
Тест SC036 — upsert business_connection.

## Трассируемость
Feature: F018
Scenario: SC036
"""

import pytest


@pytest.mark.asyncio
async def test_upsert_creates_then_updates(client):
    # create
    r = await client.post(
        "/api/v1/business/connections",
        json={"business_connection_id": "BC1", "owner_user_id": 42, "is_enabled": True},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["business_connection_id"] == "BC1"
    assert body["owner_user_id"] == 42

    # update — should not create duplicate
    r2 = await client.post(
        "/api/v1/business/connections",
        json={"business_connection_id": "BC1", "owner_user_id": 99, "is_enabled": False},
    )
    assert r2.status_code == 200
    assert r2.json()["owner_user_id"] == 99
    assert r2.json()["is_enabled"] is False

    # get
    r3 = await client.get("/api/v1/business/connections/BC1")
    assert r3.status_code == 200
    assert r3.json()["owner_user_id"] == 99
