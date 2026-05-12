"""
## Трассируемость
Feature: F001, F006, F008, F009
Scenarios: SC014, SC016, SC020, SC021, SC022
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.tasks.task_schema import TaskResponseSchema, TaskUpdateSchema
from service.tasks.task_service import TaskService


router = APIRouter()
_service = TaskService()


@router.put("/{task_id}", response_model=TaskResponseSchema)
async def update_task(
    task_id: int,
    data: TaskUpdateSchema,
    session: AsyncSession = Depends(db_connect.get_session),
) -> TaskResponseSchema:
    task = await _service.update(
        session,
        task_id,
        title=data.title,
        text=data.text,
        deadline=data.deadline,
        direction_id=data.direction_id,
        planned_start_at=data.planned_start_at,
        planned_end_at=data.planned_end_at,
        unset_direction=data.unset_direction,
        unset_planned=data.unset_planned,
    )
    payload = await _service.to_response(session, task)
    return TaskResponseSchema(**payload)
