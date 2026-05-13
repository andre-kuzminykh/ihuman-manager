"""
POST /api/v1/tasks/{id}/llm-edit — естественный язык меняет поля задачи.

## Трассируемость
Feature: F017
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.tasks.task_schema import TaskResponseSchema
from service.extractor.extractor_service import ExtractorService
from service.tasks.task_service import TaskService


router = APIRouter()
_service = TaskService()
_extractor = ExtractorService()


class LLMEditTaskSchema(BaseModel):
    instruction: str = Field(..., min_length=1, max_length=2000)


@router.post("/{task_id}/llm-edit", response_model=TaskResponseSchema)
async def llm_edit_task(
    task_id: int,
    data: LLMEditTaskSchema,
    session: AsyncSession = Depends(db_connect.get_session),
) -> TaskResponseSchema:
    task = await _service.get_or_404(session, task_id)
    current = {
        "title": task.title,
        "description": task.description,
        "deadline": task.deadline.isoformat() if task.deadline else None,
        "priority": task.priority,
    }
    updated = await _extractor.apply_edit(current, data.instruction)

    new_deadline: datetime | None = None
    if updated.get("deadline"):
        try:
            new_deadline = datetime.fromisoformat(updated["deadline"])
        except (TypeError, ValueError):
            new_deadline = None

    task = await _service.update(
        session,
        task_id,
        title=updated.get("title"),
        description=updated.get("description"),
        deadline=new_deadline,
        priority=updated.get("priority"),
    )
    payload = await _service.to_response(session, task)
    return TaskResponseSchema(**payload)
