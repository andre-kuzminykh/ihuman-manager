"""
PendingTasks endpoints.

## Трассируемость
Feature: F005
Scenarios: SC012, SC014
"""

from fastapi import APIRouter

from api.v1.endpoints.pending_tasks.get import router as get_router
from api.v1.endpoints.pending_tasks.put import router as put_router
from api.v1.endpoints.pending_tasks.actions import router as actions_router


router = APIRouter(prefix="/pending-tasks", tags=["pending-tasks"])
router.include_router(get_router)
router.include_router(put_router)
router.include_router(actions_router)

__all__ = ["router"]
