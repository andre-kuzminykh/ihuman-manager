"""
## Трассируемость
Feature: F004
Scenarios: SC009, SC010
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from service.tasks.task_favorite_service import TaskFavoriteService


router = APIRouter()
_service = TaskFavoriteService()


class _FavoriteBody(BaseModel):
    user_id: int


@router.post("/{task_id}/favorite", status_code=status.HTTP_200_OK)
async def add_favorite(
    task_id: int,
    body: _FavoriteBody,
    session: AsyncSession = Depends(db_connect.get_session),
) -> dict:
    added = await _service.add(session, user_id=body.user_id, task_id=task_id)
    return {"task_id": task_id, "user_id": body.user_id, "is_favorite": True, "added": added}


@router.delete("/{task_id}/favorite", status_code=status.HTTP_200_OK)
async def remove_favorite(
    task_id: int,
    body: _FavoriteBody,
    session: AsyncSession = Depends(db_connect.get_session),
) -> dict:
    removed = await _service.remove(session, user_id=body.user_id, task_id=task_id)
    return {"task_id": task_id, "user_id": body.user_id, "is_favorite": False, "removed": removed}
