"""
Тест SC003 — пустой текст → HTTP 422.

## Трассируемость
Feature: F001
Scenario: SC003
"""

import pytest


@pytest.mark.asyncio
async def test_empty_text_via_api(client):
    response = await client.post(
        "/api/v1/tasks",
        json={"user_id": 42, "text": "   "},
    )
    assert response.status_code == 422
