"""
Stock Sniper Bot

A sophisticated algorithmic trading alert system that identifies undervalued stocks
using fundamental analysis, statistical methods, and technical triggers.

Main Components:
- config: Configuration and watchlist management
- core: Safety checks, valuation strategies, and scanning logic
- interface: Telegram bot integration and alert management
- main: Scheduler and entry point

Quick Start:
    >>> from app.engines.stock_sniper.core import get_scanner
    >>> from app.engines.stock_sniper.config import WATCHLIST
    >>>
    >>> scanner = get_scanner()
    >>> signals = scanner.scan_multiple(WATCHLIST)
    >>> for signal in signals:
    ...     print(scanner.format_signal(signal))

For more information, see README.md
"""

__version__ = '1.0.0'
__author__ = 'Senior Python Developer & Quantitative Analyst'

# Import main components for easy access
from .config import WATCHLIST, get_all_tickers, get_sector
from .core import get_scanner, get_safety_manager, SniperSignal
from .interface import get_telegram_bot

__all__ = [
    'WATCHLIST',
    'get_all_tickers',
    'get_sector',
    'get_scanner',
    'get_safety_manager',
    'get_telegram_bot',
    'SniperSignal',
]
