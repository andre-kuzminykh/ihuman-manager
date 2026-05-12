"""
Тест SC013 — детектор тега бота.

## Трассируемость
Feature: F005
Scenario: SC013
"""

from unittest.mock import MagicMock

from core.config import config
from node.chat.code.chat_message_code import _is_bot_mentioned


def _msg(text: str) -> MagicMock:
    m = MagicMock()
    m.text = text
    m.caption = None
    return m


def test_detects_bot_mention(monkeypatch):
    monkeypatch.setattr(config, "BOT_USERNAME", "hmnd_taskbot")
    assert _is_bot_mentioned(_msg("@hmnd_taskbot подготовь презу"))
    assert _is_bot_mentioned(_msg("эй, @HMND_TASKBOT, давай"))
    assert not _is_bot_mentioned(_msg("@other_bot ага"))
    assert not _is_bot_mentioned(_msg("обычное сообщение"))
