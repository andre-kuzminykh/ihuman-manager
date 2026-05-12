"""
core — общий слой бота: конфиг, loader, vocab.
"""

from core.config import config
from core.loader import bot, dp
from core import vocab

__all__ = ["config", "bot", "dp", "vocab"]
