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

        self.analysis_last_run: Optional[datetime] = None
        self.analysis_total_runs: int = 0


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
            from app.services.alert_store import get_stock_alerts, save_stock_alerts

            scanner = get_scanner()
            signals = await asyncio.to_thread(
                scanner.scan_multiple, WATCHLIST, False, False
            )

            # Upsert each signal into the alerts store (overwrite per ticker)
            existing = get_stock_alerts().get("alerts", {})
            for sig in signals:
                existing[sig.ticker] = {
                    "timestamp": sig.timestamp.isoformat(),
                    "method": sig.strategy_result.method_name,
                    "time_horizon": sig.strategy_result.time_horizon.value,
                    "score": sig.strategy_result.score,
                    "price": sig.strategy_result.current_price,
                    "target": sig.strategy_result.target_price,
                    "reason": sig.strategy_result.reason,
                    "ema_value": (
                        sig.trigger_result.ema_value
                        if sig.trigger_result else None
                    ),
                }
            if signals:
                save_stock_alerts(existing)

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
            from app.services.alert_store import get_crypto_alerts, save_crypto_alerts

            monitor = CryptoMonitor()
            signals = await asyncio.to_thread(
                monitor.scan_multiple, CRYPTO_WATCHLIST
            )

            # Upsert each signal into the alerts store (overwrite per symbol)
            existing = get_crypto_alerts().get("alerts", {})
            for sig in signals:
                existing[sig.symbol] = {
                    "symbol": sig.symbol,
                    "name": sig.name,
                    "category": sig.category,
                    "current_price": sig.current_price,
                    "valuation_method": sig.valuation_method,
                    "valuation_score": sig.valuation_score,
                    "fair_value_estimate": sig.fair_value_estimate,
                    "discount_percentage": sig.discount_percentage,
                    "trigger_type": sig.trigger_type,
                    "trigger_description": sig.trigger_description,
                    "rsi": sig.rsi,
                    "bollinger_position": sig.bollinger_position,
                    "change_24h": sig.change_24h,
                    "change_7d": sig.change_7d,
                    "severity": sig.severity,
                    "confidence": sig.confidence,
                    "combined_score": sig.combined_score,
                    "timestamp": sig.timestamp.isoformat(),
                }
            if signals:
                save_crypto_alerts(existing)

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

    async def _run_market_analysis(self):
        """Run AI market analysis using recent news headlines."""
        try:
            from app.engines.market_analysis.analyzer import MarketAnalyzer

            analyzer = MarketAnalyzer()
            await analyzer.run_all()

            self.stats.analysis_last_run = datetime.now()
            self.stats.analysis_total_runs += 1

            logger.info("Market analysis complete")
        except Exception as e:
            logger.error(f"Market analysis error: {e}", exc_info=True)

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
        self.scheduler.add_job(
            self._run_market_analysis,
            "interval",
            minutes=settings.analysis_scan_interval,
            id="market_analysis",
            name="Market Analysis",
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
