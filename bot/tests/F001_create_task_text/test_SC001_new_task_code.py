"""
Тест SC001 — NewTaskCode вызывает API и возвращает answer_name='task_created'.

## Трассируемость
Feature: F001
Scenario: SC001
"""

from unittest.mock import AsyncMock

import pytest

from node.task.code.new_task_code import NewTaskCode


@pytest.mark.asyncio
async def test_new_task_code_creates_task(mock_state):
    api = AsyncMock()
    api.create = AsyncMock(return_value={"id": 1, "status": "todo", "title": "Test"})
    code = NewTaskCode(api=api)
    result = await code.run(
        {"user_id": 42, "text": "Подготовить отчёт до пятницы", "source_kind": "text"},
        mock_state,
    )
    assert result["answer_name"] == "task_created"
    api.create.assert_awaited_once()
    kwargs = api.create.call_args.kwargs
    assert kwargs["user_id"] == 42
    assert kwargs["text"] == "Подготовить отчёт до пятницы"
