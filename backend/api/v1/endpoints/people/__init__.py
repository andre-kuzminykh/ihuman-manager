"""
People endpoints.

## Трассируемость
Feature: F020
"""

from fastapi import APIRouter

from api.v1.endpoints.people.touch import router as touch_router
from api.v1.endpoints.people.get import router as get_router


router = APIRouter(prefix="/people", tags=["people"])
router.include_router(touch_router)
router.include_router(get_router)

__all__ = ["router"]
