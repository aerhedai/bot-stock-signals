"""
Crypto Sniper Bot

A cryptocurrency price monitoring and alert system that detects significant
price movements, volume spikes, and technical indicator signals.

Main Components:
- config: Configuration and crypto watchlist management
- core: Price monitoring, technical indicators, and signal detection
- interface: Telegram bot integration and alert management
- main: Scheduler and entry point

Quick Start:
    >>> from app.engines.crypto_sniper.core import CryptoMonitor
    >>> from app.engines.crypto_sniper.config import CRYPTO_WATCHLIST
    >>>
    >>> monitor = CryptoMonitor()
    >>> signals = monitor.scan_multiple(CRYPTO_WATCHLIST)
    >>> for signal in signals:
    ...     print(f"{signal.name}: {signal.description}")

For more information, see README.md
"""

__version__ = '1.0.0'
__author__ = 'Crypto Trading Analyst'

# Import main components for easy access
from .config import CRYPTO_WATCHLIST, settings
from .core import CryptoMonitor, CryptoSignal, TechnicalIndicators
from .interface import CryptoTelegramBot

__all__ = [
    'CRYPTO_WATCHLIST',
    'settings',
    'CryptoMonitor',
    'CryptoSignal',
    'TechnicalIndicators',
    'CryptoTelegramBot',
]
