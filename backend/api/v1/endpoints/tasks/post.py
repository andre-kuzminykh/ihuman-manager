"""
## Трассируемость
Feature: F001, F002
Scenarios: SC001, SC002, SC003, SC004
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.tasks.task_schema import TaskCreateSchema, TaskResponseSchema
from service.tasks.task_service import TaskService


router = APIRouter()
_service = TaskService()


@router.post("", response_model=TaskResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreateSchema,
    session: AsyncSession = Depends(db_connect.get_session),
) -> TaskResponseSchema:
    task = await _service.create_from_text(
        session,
        user_id=data.user_id,
        text=data.text,
        chat_id=data.chat_id,
        source_message_id=data.source_message_id,
        source_kind=data.source_kind,
        title=data.title,
        deadline=data.deadline,
        direction_id=data.direction_id,
    )
    payload = await _service.to_response(session, task)
    return TaskResponseSchema(**payload)
