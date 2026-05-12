"""
core — общие модули бэкенда: конфиг, БД, исключения, FastAPI-приложение.
"""

from core.config import config
from core.database import db_connect
from core.exceptions import (
    AppException,
    NotFoundError,
    ValidationError,
    ConflictError,
    InvalidTransitionError,
)
from core.loader import app

__all__ = [
    "config",
    "db_connect",
    "app",
    "AppException",
    "NotFoundError",
    "ValidationError",
    "ConflictError",
    "InvalidTransitionError",
]
