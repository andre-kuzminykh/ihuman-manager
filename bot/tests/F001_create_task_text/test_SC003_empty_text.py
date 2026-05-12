"""
Тест SC003 — пустой текст → answer_name='task_empty_error', API не дёргается.

## Трассируемость
Feature: F001
Scenario: SC003
"""

from unittest.mock import AsyncMock

import pytest

from node.task.code.new_task_code import NewTaskCode


@pytest.mark.asyncio
async def test_new_task_code_empty_text(mock_state):
    api = AsyncMock()
    code = NewTaskCode(api=api)
    result = await code.run({"user_id": 42, "text": "   ", "source_kind": "text"}, mock_state)
    assert result["answer_name"] == "task_empty_error"
    api.create.assert_not_called()
