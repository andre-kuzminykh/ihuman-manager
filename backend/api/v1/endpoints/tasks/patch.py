"""
## Трассируемость
Feature: F003
Scenarios: SC006, SC008
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.tasks.task_schema import TaskResponseSchema, TaskStatusUpdateSchema
from service.tasks.task_service import TaskService


router = APIRouter()
_service = TaskService()


@router.patch("/{task_id}/status", response_model=TaskResponseSchema)
async def transition_status(
    task_id: int,
    data: TaskStatusUpdateSchema,
    session: AsyncSession = Depends(db_connect.get_session),
) -> TaskResponseSchema:
    task = await _service.transition_status(
        session,
        task_id,
        to=data.to,
        changed_by=data.changed_by,
        reason=data.reason,
    )
    payload = await _service.to_response(session, task)
    return TaskResponseSchema(**payload)
