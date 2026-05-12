"""
core.exceptions — иерархия доменных ошибок.

Маппятся в HTTP-статусы в api.v1.exception_handlers.
"""

from __future__ import annotations


class AppException(Exception):
    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code


class NotFoundError(AppException):
    status_code = 404
    code = "not_found"


class ValidationError(AppException):
    status_code = 422
    code = "validation_error"


class ConflictError(AppException):
    status_code = 409
    code = "conflict"


class InvalidTransitionError(ValidationError):
    code = "invalid_transition"
