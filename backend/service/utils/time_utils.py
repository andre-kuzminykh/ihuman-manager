"""
service.utils.time_utils — работа с MSK и дефолтами времени.

## Трассируемость
Feature: F001 (BR001), F007 (BR019)
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytz

from core.config import config

MSK = pytz.timezone("Europe/Moscow")


def now_msk() -> datetime:
    return datetime.now(MSK)


def today_msk_default_deadline(now: datetime | None = None) -> datetime:
    n = (now or now_msk()).astimezone(MSK)
    return n.replace(hour=config.DEFAULT_DEADLINE_HOUR_MSK, minute=0, second=0, microsecond=0)


def to_msk(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return MSK.localize(dt)
    return dt.astimezone(MSK)


def start_of_msk_day(dt: datetime | None = None) -> datetime:
    n = (dt or now_msk()).astimezone(MSK)
    return n.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_msk_day(dt: datetime | None = None) -> datetime:
    return start_of_msk_day(dt) + timedelta(days=1) - timedelta(microseconds=1)
