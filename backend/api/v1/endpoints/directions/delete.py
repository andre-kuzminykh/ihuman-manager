"""
## Трассируемость
Feature: F009
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from service.directions.direction_service import DirectionService


router = APIRouter()
_service = DirectionService()


@router.delete("/{direction_id}")
async def delete_direction(
    direction_id: int,
    session: AsyncSession = Depends(db_connect.get_session),
) -> dict:
    await _service.delete(session, direction_id)
    return {"deleted": True, "direction_id": direction_id}
