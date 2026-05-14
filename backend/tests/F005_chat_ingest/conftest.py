"""
Фикстуры F005: мокаем ExtractorService.classify_message,
чтобы тесты не ходили в OpenAI.
"""

from __future__ import annotations

import pytest

from service.extractor.extractor_service import ExtractorService


@pytest.fixture
def classify_as_task(monkeypatch):
    """Имитируем ВСЕ ветки экстрактора: classify_message (legacy),
    is_message_taskful + extract_multiple (двухступенчатый pipeline).
    """

    async def fake_classify(self, text, *, context_messages=None):
        return {
            "is_task": True,
            "title": text[:80],
            "deadline": None,
            "confidence": 0.9,
            "rationale": "mock",
        }

    async def fake_taskful(self, text, *, context_messages=None):
        return True

    async def fake_extract(self, text, *, context_messages=None, sender_display=None):
        return [
            {
                "title": text[:80] or "Задача",
                "description": None,
                "text": text,
                "deadline": None,
                "priority": "medium",
                "confidence": 0.9,
            }
        ]

    monkeypatch.setattr(ExtractorService, "classify_message", fake_classify)
    monkeypatch.setattr(ExtractorService, "is_message_taskful", fake_taskful)
    monkeypatch.setattr(ExtractorService, "extract_multiple", fake_extract)


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

    async def fake_taskful(self, text, *, context_messages=None):
        return False

    async def fake_extract(self, text, *, context_messages=None, sender_display=None):
        return []

    monkeypatch.setattr(ExtractorService, "classify_message", fake_classify)
    monkeypatch.setattr(ExtractorService, "is_message_taskful", fake_taskful)
    monkeypatch.setattr(ExtractorService, "extract_multiple", fake_extract)
