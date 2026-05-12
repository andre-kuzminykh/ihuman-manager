"""
## Трассируемость
Feature: F009
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from service.directions.direction_service import DirectionService


router = APIRouter()
_service = DirectionService()


@router.delete("/{direction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_direction(
    direction_id: int,
    session: AsyncSession = Depends(db_connect.get_session),
) -> None:
    await _service.delete(session, direction_id)
