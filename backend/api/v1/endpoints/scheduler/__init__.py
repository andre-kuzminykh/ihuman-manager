"""
Scheduler endpoint.

## Трассируемость
Feature: F003, F006, F007
"""

from fastapi import APIRouter

from api.v1.endpoints.scheduler.tick import router as tick_router


router = APIRouter(prefix="/scheduler", tags=["scheduler"])
router.include_router(tick_router)

__all__ = ["router"]
