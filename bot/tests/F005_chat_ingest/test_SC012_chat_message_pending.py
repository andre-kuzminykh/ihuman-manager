"""
Тест SC012 — ChatMessageCode → 'pending_card_dm' для подписанного чата.

## Трассируемость
Feature: F005
Scenario: SC012
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from node.chat.code.chat_message_code import ChatMessageCode


def _message(text="Надо собрать отчёт", mentioned=False):
    m = MagicMock()
    m.text = text
    m.caption = None
    m.message_id = 1
    m.date = datetime.now(timezone.utc)
    m.chat = MagicMock()
    m.chat.id = -1001
    m.from_user = MagicMock()
    m.from_user.id = 7
    m.from_user.username = "alex"
    m.from_user.is_bot = False
    return m


@pytest.mark.asyncio
async def test_pending_card_for_subscribed_chat():
    chats_api = AsyncMock()
    chats_api.ingest_message = AsyncMock(
        return_value={"decision": "pending_created", "pending_task_id": 9}
    )
    pending_api = AsyncMock()
    pending_api.get = AsyncMock(return_value={"id": 9, "owner_user_id": 42, "draft": {}})
    tasks_api = AsyncMock()

    code = ChatMessageCode(chats_api=chats_api, pending_api=pending_api, tasks_api=tasks_api)
    result = await code.run(_message())
    assert result["answer_name"] == "pending_card_dm"
    assert result["data"]["pending"]["id"] == 9


@pytest.mark.asyncio
async def test_ignored_when_not_subscribed():
    chats_api = AsyncMock()
    chats_api.ingest_message = AsyncMock(return_value={"decision": "not_subscribed"})
    code = ChatMessageCode(chats_api=chats_api, pending_api=AsyncMock(), tasks_api=AsyncMock())
    result = await code.run(_message())
    assert result["answer_name"] == "noop"
