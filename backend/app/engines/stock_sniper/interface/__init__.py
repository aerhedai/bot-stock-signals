"""Interface package for Stock Sniper Bot.

Exports:
    - TelegramBot, get_telegram_bot
    - AlertHistory
"""

from .telegram_bot import TelegramBot, AlertHistory, get_telegram_bot

__all__ = [
    'TelegramBot',
    'AlertHistory',
    'get_telegram_bot',
]
