"""
Тест SC034 — одна задача в сообщении.

## Трассируемость
Feature: F015
Scenario: SC034
"""

import pytest

from service.extractor.extractor_service import ExtractorService


@pytest.mark.asyncio
async def test_batch_with_single_task(client, monkeypatch):
    async def fake_extract(self, text, *, context_messages=None):
        return [
            {"title": "Позвонить Алине", "text": "Позвонить Алине", "deadline": None, "confidence": 0.9}
        ]

    monkeypatch.setattr(ExtractorService, "extract_multiple", fake_extract)
    resp = await client.post(
        "/api/v1/tasks/batch",
        json={"user_id": 99, "text": "позвонить алине"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 1
    assert body["tasks"][0]["title"] == "Позвонить Алине"
