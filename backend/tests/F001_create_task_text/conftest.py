"""
Фикстуры F001 — фиксированное "сейчас" для воспроизводимости парсинга дат.
"""

from __future__ import annotations

from datetime import datetime

import pytest
import pytz

MSK = pytz.timezone("Europe/Moscow")


@pytest.fixture
def fixed_now() -> datetime:
    # среда 2026-05-12 10:00 МСК
    return MSK.localize(datetime(2026, 5, 12, 10, 0, 0))
