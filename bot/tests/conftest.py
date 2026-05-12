"""
conftest — глобальные мок-фикстуры (без реальных Telegram/HTTP).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = 42
    user.username = "ceo"
    user.is_bot = False
    return user


@pytest.fixture
def mock_message(mock_user):
    msg = AsyncMock()
    msg.from_user = mock_user
    msg.chat = MagicMock()
    msg.chat.id = 42
    msg.chat.type = "private"
    msg.chat.title = None
    msg.text = "/new Подготовить отчёт до пятницы"
    msg.message_id = 1
    msg.answer = AsyncMock()
    return msg


@pytest.fixture
def mock_state():
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    state.set_data = AsyncMock()
    state.clear = AsyncMock()
    state.set_state = AsyncMock()
    state.update_data = AsyncMock()
    return state
