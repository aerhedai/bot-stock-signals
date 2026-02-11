"""
News Monitor Module

Real-time financial news monitoring system for stocks and crypto.
Fetches news from Finnhub API and sends to separate Telegram topics.
"""

__version__ = '1.0.0'

from app.engines.news_monitor.fetcher import NewsFetcher
from app.engines.news_monitor.monitor import NewsMonitor

__all__ = ['NewsFetcher', 'NewsMonitor']
