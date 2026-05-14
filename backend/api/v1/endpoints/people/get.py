"""
GET /api/v1/people — список контактов.

## Трассируемость
Feature: F020
Scenarios: SC041
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.people.person_schema import PersonResponseSchema
from service.people.person_service import PersonService


router = APIRouter()
_service = PersonService()


@router.get("/", response_model=list[PersonResponseSchema])
async def list_people(
    session: AsyncSession = Depends(db_connect.get_session),
) -> list[PersonResponseSchema]:
    items = await _service.list_all(session)
    return [PersonResponseSchema.model_validate(p) for p in items]
