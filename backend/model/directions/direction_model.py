"""
DirectionModel — направление (категория) задач.

## Трассируемость
Feature: F009
Scenarios: SC022, SC023, SC024

(user_id, name) уникально (case-insensitive — обеспечивается LOWER(name) индексом).
"""

from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from model.base_model import Base, BaseModel


class DirectionModel(Base, BaseModel):
    __tablename__ = "directions"

    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_directions_user_name"),
    )
