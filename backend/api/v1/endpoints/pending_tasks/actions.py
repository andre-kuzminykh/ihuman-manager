"""
## Трассируемость
Feature: F005
Scenarios: SC012, SC013, SC014
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.chats.pending_task_schema import PendingTaskResponseSchema
from service.chats.pending_task_service import PendingTaskService


router = APIRouter()
_service = PendingTaskService()


@router.post("/{pending_id}/approve", response_model=PendingTaskResponseSchema)
async def approve_pending(
    pending_id: int,
    session: AsyncSession = Depends(db_connect.get_session),
) -> PendingTaskResponseSchema:
    obj = await _service.approve(session, pending_id)
    return PendingTaskResponseSchema.model_validate(obj)


@router.post("/{pending_id}/reject", response_model=PendingTaskResponseSchema)
async def reject_pending(
    pending_id: int,
    session: AsyncSession = Depends(db_connect.get_session),
) -> PendingTaskResponseSchema:
    obj = await _service.reject(session, pending_id)
    return PendingTaskResponseSchema.model_validate(obj)
