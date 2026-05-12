"""
Тест SC019 — пустой дайджест.

## Трассируемость
Feature: F007
Scenario: SC019
"""

import pytest


@pytest.mark.asyncio
async def test_digest_empty(client):
    response = await client.get("/api/v1/digest/777")
    assert response.status_code == 200
    body = response.json()
    assert body["is_empty"] is True
    assert body["total"] == 0
