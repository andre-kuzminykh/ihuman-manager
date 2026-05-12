"""
Фикстуры F005: мокаем ExtractorService.classify_message,
чтобы тесты не ходили в OpenAI.
"""

from __future__ import annotations

import pytest

from service.extractor.extractor_service import ExtractorService


@pytest.fixture
def classify_as_task(monkeypatch):
    async def fake_classify(self, text, *, context_messages=None):
        return {
            "is_task": True,
            "title": text[:80],
            "deadline": None,
            "confidence": 0.9,
            "rationale": "mock",
        }

    monkeypatch.setattr(ExtractorService, "classify_message", fake_classify)


@pytest.fixture
def classify_as_chitchat(monkeypatch):
    async def fake_classify(self, text, *, context_messages=None):
        return {
            "is_task": False,
            "title": None,
            "deadline": None,
            "confidence": 0.9,
            "rationale": "mock",
        }

    monkeypatch.setattr(ExtractorService, "classify_message", fake_classify)
