"""
## Трассируемость
Feature: F005
Scenarios: SC014
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.chats.pending_task_schema import (
    PendingTaskResponseSchema,
    PendingTaskUpdateSchema,
)
from service.chats.pending_task_service import PendingTaskService


router = APIRouter()
_service = PendingTaskService()


@router.put("/{pending_id}", response_model=PendingTaskResponseSchema)
async def update_pending(
    pending_id: int,
    data: PendingTaskUpdateSchema,
    session: AsyncSession = Depends(db_connect.get_session),
) -> PendingTaskResponseSchema:
    obj = await _service.update_draft(
        session,
        pending_id,
        draft=data.draft,
        title=data.title,
        text=data.text,
        deadline=data.deadline,
        direction_id=data.direction_id,
    )
    return PendingTaskResponseSchema.model_validate(obj)
