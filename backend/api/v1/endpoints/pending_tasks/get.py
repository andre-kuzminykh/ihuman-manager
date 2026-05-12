"""
## Трассируемость
Feature: F005
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.chats.pending_task_schema import PendingTaskResponseSchema
from service.chats.pending_task_service import PendingTaskService


router = APIRouter()
_service = PendingTaskService()


@router.get("/", response_model=list[PendingTaskResponseSchema])
async def list_pending(
    owner_user_id: int,
    only_unapproved: bool = True,
    session: AsyncSession = Depends(db_connect.get_session),
) -> list[PendingTaskResponseSchema]:
    items = await _service.list_for_owner(
        session, owner_user_id, only_unapproved=only_unapproved
    )
    return [PendingTaskResponseSchema.model_validate(p) for p in items]


@router.get("/{pending_id}", response_model=PendingTaskResponseSchema)
async def get_pending(
    pending_id: int,
    session: AsyncSession = Depends(db_connect.get_session),
) -> PendingTaskResponseSchema:
    obj = await _service.get_or_404(session, pending_id)
    return PendingTaskResponseSchema.model_validate(obj)
