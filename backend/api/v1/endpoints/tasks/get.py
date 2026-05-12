"""
## Трассируемость
Feature: F003, F004, F007, F009
Scenarios: SC006, SC009, SC018, SC023
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from model.enums import TaskStatus
from schema.tasks.task_schema import TaskListItemSchema, TaskResponseSchema
from service.tasks.task_service import TaskService


router = APIRouter()
_service = TaskService()


@router.get("", response_model=list[TaskListItemSchema])
async def list_tasks(
    user_id: int,
    status: Annotated[list[TaskStatus] | None, Query()] = None,
    direction_id: int | None = None,
    favorite_only: bool = False,
    deadline_before: datetime | None = None,
    deadline_after: datetime | None = None,
    session: AsyncSession = Depends(db_connect.get_session),
) -> list[TaskListItemSchema]:
    items = await _service.list_for_user(
        session,
        user_id,
        statuses=status,
        direction_id=direction_id,
        favorite_only=favorite_only,
        deadline_before=deadline_before,
        deadline_after=deadline_after,
    )
    return [TaskListItemSchema(**item) for item in items]


@router.get("/{task_id}", response_model=TaskResponseSchema)
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(db_connect.get_session),
) -> TaskResponseSchema:
    task = await _service.get_or_404(session, task_id)
    payload = await _service.to_response(session, task)
    return TaskResponseSchema(**payload)
