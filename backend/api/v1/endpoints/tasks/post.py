"""
## Трассируемость
Feature: F001, F002, F010
Scenarios: SC001, SC002, SC003, SC004, SC025, SC026
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.tasks.task_schema import TaskCreateSchema, TaskResponseSchema
from service.tasks.task_service import TaskService


router = APIRouter()
_service = TaskService()


@router.post("", response_model=TaskResponseSchema)
async def create_task(
    data: TaskCreateSchema,
    response: Response,
    session: AsyncSession = Depends(db_connect.get_session),
) -> TaskResponseSchema:
    task, is_duplicate = await _service.create_or_find_duplicate(
        session,
        user_id=data.user_id,
        text=data.text,
        chat_id=data.chat_id,
        source_message_id=data.source_message_id,
        source_kind=data.source_kind,
        title=data.title,
        deadline=data.deadline,
        direction_id=data.direction_id,
        force=data.force,
    )
    payload = await _service.to_response(session, task)
    payload["is_duplicate"] = is_duplicate
    response.status_code = 200 if is_duplicate else 201
    return TaskResponseSchema(**payload)
