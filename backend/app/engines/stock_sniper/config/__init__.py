"""Configuration package for Stock Sniper Bot."""

from .settings import *
from .tickers import WATCHLIST, get_all_tickers, get_sector

__all__ = ['WATCHLIST', 'get_all_tickers', 'get_sector']
