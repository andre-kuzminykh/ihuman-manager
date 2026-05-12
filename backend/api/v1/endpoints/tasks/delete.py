"""
## Трассируемость
Feature: F003
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from service.tasks.task_service import TaskService


router = APIRouter()
_service = TaskService()


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(db_connect.get_session),
) -> None:
    await _service.soft_delete(session, task_id)
