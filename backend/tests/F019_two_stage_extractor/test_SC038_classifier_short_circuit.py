"""
Тест SC038 — classifier=false → decomposer не вызывается.

## Трассируемость
Feature: F019
Scenario: SC038
"""

import pytest

from service.extractor.extractor_service import ExtractorService


@pytest.mark.asyncio
async def test_classifier_short_circuits_decomposer(monkeypatch):
    service = ExtractorService(openai_api_key="dummy")
    # притворимся, что клиент есть (иначе пойдёт heuristic-фоллбек)
    service._client = object()

    async def fake_classifier(self, text, *, context_messages=None):
        return False

    called = {"n": 0}

    async def fake_decomposer(*args, **kwargs):
        called["n"] += 1
        return []

    monkeypatch.setattr(ExtractorService, "is_message_taskful", fake_classifier)
    # decomposer = chat.completions.create — заменим клиент целиком
    class _Stub:
        class chat:
            class completions:
                @staticmethod
                async def create(**kwargs):
                    called["n"] += 1
                    return None

    service._client = _Stub()

    result = await service.extract_multiple("привет как дела")
    assert result == []
    assert called["n"] == 0, "decomposer не должен был вызываться"


@pytest.mark.asyncio
async def test_classifier_true_runs_decomposer(monkeypatch):
    service = ExtractorService(openai_api_key="dummy")

    async def fake_classifier(self, text, *, context_messages=None):
        return True

    monkeypatch.setattr(ExtractorService, "is_message_taskful", fake_classifier)

    class _Resp:
        class _Choice:
            class _Msg:
                content = '{"tasks":[{"title":"A","text":"A","priority":"high","confidence":0.9},{"title":"B","text":"B","priority":"medium","confidence":0.8}]}'
            message = _Msg()
        choices = [_Choice()]

    class _Stub:
        class chat:
            class completions:
                @staticmethod
                async def create(**kwargs):
                    return _Resp()

    service._client = _Stub()
    result = await service.extract_multiple("надо A и B")
    assert len(result) == 2
    titles = {t["title"] for t in result}
    assert titles == {"A", "B"}
