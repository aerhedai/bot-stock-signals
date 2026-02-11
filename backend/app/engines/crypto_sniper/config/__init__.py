"""
Crypto Sniper Configuration Module

Exports all configuration settings and crypto watchlist.
"""

from .settings import *
from .crypto_list import CRYPTO_WATCHLIST

__all__ = ['CRYPTO_WATCHLIST', 'settings']
