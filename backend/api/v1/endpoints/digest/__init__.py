"""
Digest endpoint.

## Трассируемость
Feature: F007
"""

from fastapi import APIRouter

from api.v1.endpoints.digest.get import router as get_router


router = APIRouter(prefix="/digest", tags=["digest"])
router.include_router(get_router)

__all__ = ["router"]
