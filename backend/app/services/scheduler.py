"""
APScheduler-based service for running stock, crypto, and news scan jobs.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings

logger = logging.getLogger(__name__)


class ScanStats:
    """Tracks scan statistics across all services."""

    def __init__(self):
        self.stock_last_run: Optional[datetime] = None
        self.stock_total_runs: int = 0
        self.stock_last_signals: int = 0

        self.crypto_last_run: Optional[datetime] = None
        self.crypto_total_runs: int = 0
        self.crypto_last_signals: int = 0

        self.news_last_run: Optional[datetime] = None
        self.news_total_runs: int = 0
        self.news_last_articles: int = 0


class SchedulerService:
    """Manages scheduled scan jobs using APScheduler."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.stats = ScanStats()
        self._running = False

    async def _run_stock_scan(self):
        """Run stock scan job in a thread (yfinance is sync)."""
        try:
            from app.engines.stock_sniper.config import WATCHLIST
            from app.engines.stock_sniper.core import get_scanner

            scanner = get_scanner()
            signals = await asyncio.to_thread(
                scanner.scan_multiple, WATCHLIST, False, False
            )

            self.stats.stock_last_run = datetime.now()
            self.stats.stock_total_runs += 1
            self.stats.stock_last_signals = len(signals)

            logger.info(f"Stock scan complete: {len(signals)} signals found")
        except Exception as e:
            logger.error(f"Stock scan error: {e}", exc_info=True)

    async def _run_crypto_scan(self):
        """Run crypto scan job in a thread."""
        try:
            from app.engines.crypto_sniper.config import CRYPTO_WATCHLIST
            from app.engines.crypto_sniper.core import CryptoMonitor

            monitor = CryptoMonitor()
            signals = await asyncio.to_thread(
                monitor.scan_multiple, CRYPTO_WATCHLIST
            )

            self.stats.crypto_last_run = datetime.now()
            self.stats.crypto_total_runs += 1
            self.stats.crypto_last_signals = len(signals)

            logger.info(f"Crypto scan complete: {len(signals)} signals found")
        except Exception as e:
            logger.error(f"Crypto scan error: {e}", exc_info=True)

    async def _run_news_fetch(self):
        """Run news fetch job in a thread."""
        try:
            from app.engines.news_monitor.monitor import NewsMonitor

            monitor = NewsMonitor()
            stats = await asyncio.to_thread(monitor.run_once)

            self.stats.news_last_run = datetime.now()
            self.stats.news_total_runs += 1
            self.stats.news_last_articles = stats.get("new", 0)

            logger.info(f"News fetch complete: {stats.get('new', 0)} new articles")
        except Exception as e:
            logger.error(f"News fetch error: {e}", exc_info=True)

    def start(self):
        """Start the scheduler with configured jobs."""
        if self._running:
            return

        self.scheduler.add_job(
            self._run_stock_scan,
            "interval",
            minutes=settings.stock_scan_interval,
            id="stock_scan",
            name="Stock Sniper Scan",
        )
        self.scheduler.add_job(
            self._run_crypto_scan,
            "interval",
            minutes=settings.crypto_scan_interval,
            id="crypto_scan",
            name="Crypto Sniper Scan",
        )
        self.scheduler.add_job(
            self._run_news_fetch,
            "interval",
            minutes=settings.news_scan_interval,
            id="news_fetch",
            name="News Monitor Fetch",
        )

        self.scheduler.start()
        self._running = True
        logger.info("Scheduler started with all jobs")

    def stop(self):
        """Stop the scheduler."""
        if self._running:
            self.scheduler.shutdown(wait=False)
            self._running = False
            logger.info("Scheduler stopped")

    @property
    def is_running(self) -> bool:
        return self._running

    def get_next_run(self, job_id: str) -> Optional[datetime]:
        """Get the next scheduled run time for a job."""
        job = self.scheduler.get_job(job_id)
        if job and job.next_run_time:
            return job.next_run_time
        return None
