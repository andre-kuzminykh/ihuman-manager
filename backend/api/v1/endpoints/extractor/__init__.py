"""
Extractor endpoint.

## Трассируемость
Feature: F001, F005
"""

from fastapi import APIRouter

from api.v1.endpoints.extractor.post import router as post_router
from api.v1.endpoints.extractor.multi import router as multi_router


router = APIRouter(prefix="/extract", tags=["extractor"])
router.include_router(post_router)
router.include_router(multi_router)

__all__ = ["router"]
