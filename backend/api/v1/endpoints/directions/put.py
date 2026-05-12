"""
## Трассируемость
Feature: F009
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.directions.direction_schema import (
    DirectionResponseSchema,
    DirectionUpdateSchema,
)
from service.directions.direction_service import DirectionService


router = APIRouter()
_service = DirectionService()


@router.put("/{direction_id}", response_model=DirectionResponseSchema)
async def update_direction(
    direction_id: int,
    data: DirectionUpdateSchema,
    session: AsyncSession = Depends(db_connect.get_session),
) -> DirectionResponseSchema:
    d = await _service.update(
        session, direction_id, name=data.name, is_favorite=data.is_favorite
    )
    return DirectionResponseSchema.model_validate(d)
