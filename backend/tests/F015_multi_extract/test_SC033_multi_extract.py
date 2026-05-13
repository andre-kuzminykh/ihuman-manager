"""
Тест SC033 — несколько задач в одном сообщении.

## Трассируемость
Feature: F015
Scenario: SC033
"""

from unittest.mock import AsyncMock

import pytest

from service.extractor.extractor_service import ExtractorService
from service.tasks.task_service import TaskService


@pytest.mark.asyncio
async def test_create_many_creates_two(async_session, monkeypatch):
    async def fake_extract(self, text, *, context_messages=None):
        return [
            {"title": "Позвонить Алине", "text": "Позвонить Алине", "deadline": None, "confidence": 0.9},
            {"title": "Подготовить отчёт", "text": "Подготовить отчёт", "deadline": None, "confidence": 0.9},
        ]

    monkeypatch.setattr(ExtractorService, "extract_multiple", fake_extract)
    service = TaskService()
    extracted = await ExtractorService().extract_multiple("...")
    results = await service.create_many_from_extraction(
        async_session, user_id=1, extracted=extracted
    )
    assert len(results) == 2
    titles = {t.title for t, _ in results}
    assert "Позвонить Алине" in titles and "Подготовить отчёт" in titles


@pytest.mark.asyncio
async def test_batch_endpoint(client, monkeypatch):
    async def fake_extract(self, text, *, context_messages=None):
        return [
            {"title": "Позвонить Алине", "text": "Позвонить Алине", "deadline": None, "confidence": 0.9},
            {"title": "Подготовить отчёт", "text": "Подготовить отчёт", "deadline": None, "confidence": 0.9},
        ]

    monkeypatch.setattr(ExtractorService, "extract_multiple", fake_extract)
    resp = await client.post(
        "/api/v1/tasks/batch",
        json={"user_id": 42, "text": "позвонить алине и подготовить отчёт"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 2
    assert body["duplicates"] == 0
