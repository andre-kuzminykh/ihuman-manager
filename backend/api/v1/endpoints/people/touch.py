"""
POST /api/v1/people/touch — upsert контакта.

## Трассируемость
Feature: F020
Scenarios: SC040
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.people.person_schema import PersonResponseSchema, PersonTouchSchema
from service.people.person_service import PersonService


router = APIRouter()
_service = PersonService()


@router.post("/touch", response_model=PersonResponseSchema | None)
async def touch(
    data: PersonTouchSchema,
    session: AsyncSession = Depends(db_connect.get_session),
) -> PersonResponseSchema | None:
    person = await _service.touch(
        session,
        telegram_user_id=data.telegram_user_id,
        username=data.username,
        first_name=data.first_name,
        last_name=data.last_name,
        is_bot=data.is_bot,
        language_code=data.language_code,
        is_premium=data.is_premium,
    )
    if person is None:
        return None
    return PersonResponseSchema.model_validate(person)
