"""
Stock Sniper Bot - Main Entry Point

Orchestrates the complete scanning pipeline:
1. Loads configuration and watchlist
2. Initialises scanner and Telegram bot
3. Runs scheduled scans every N minutes
4. Sends alerts for valid signals

Run with: python stock_sniper/main.py
"""

import logging
import time
import schedule
from datetime import datetime
from typing import List

from app.engines.stock_sniper.config import settings, WATCHLIST
from app.engines.stock_sniper.core import get_scanner, SniperSignal
from app.engines.stock_sniper.interface import get_telegram_bot

# Ensure log directory exists
from pathlib import Path
log_file = Path(settings.LOG_FILE)
log_file.parent.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format=settings.LOG_FORMAT,
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class SniperBot:
    """
    Main bot orchestrator that runs scheduled scans and sends alerts.
    """

    def __init__(self):
        """Initialise the sniper bot."""
        logger.info("=" * 60)
        logger.info("Initialising Stock Sniper Bot")
        logger.info("=" * 60)

        # Load components
        self.scanner = get_scanner()
        self.telegram = get_telegram_bot()
        self.watchlist = WATCHLIST

        # Statistics
        self.total_scans = 0
        self.total_signals = 0
        self.total_alerts_sent = 0
        self.start_time = datetime.now()

        logger.info(f"Configuration loaded:")
        logger.info(f"  Watchlist: {len(self.watchlist)} tickers")
        logger.info(f"  Scan interval: {settings.SCAN_INTERVAL_MINUTES} minutes")
        logger.info(f"  Alert cooldown: {settings.ALERT_COOLDOWN_DAYS} days")
        logger.info(f"  Market checks: {'Enabled' if settings.MARKET_CHECK_ENABLED else 'Disabled'}")
        logger.info(f"  Earnings checks: {'Enabled' if settings.EARNINGS_CHECK_ENABLED else 'Disabled'}")
        logger.info("=" * 60)

    def scan_job(self):
        """
        Execute a complete scan of the watchlist.

        This is the main job that runs on schedule.
        """
        scan_start = datetime.now()
        logger.info("\n" + "=" * 60)
        logger.info(f"Starting scheduled scan #{self.total_scans + 1}")
        logger.info(f"Time: {scan_start.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)

        try:
            # Run scan
            signals = self.scanner.scan_multiple(
                tickers=self.watchlist,
                verbose=False,  # Set to True for detailed logs
                stop_on_signal=False  # Scan all tickers
            )

            self.total_scans += 1
            self.total_signals += len(signals)

            # Send alerts for valid signals
            if signals:
                logger.info(f"\n✓ Found {len(signals)} valid signal(s)!")

                # Group signals by time horizon
                from app.engines.stock_sniper.core.strategies import TimeHorizon
                horizon_counts = {
                    TimeHorizon.SHORT_TERM: [],
                    TimeHorizon.SWING_TRADE: [],
                    TimeHorizon.LONG_TERM: []
                }

                for signal in signals:
                    for horizon in signal.categorized_strategies.keys():
                        if signal.ticker not in [s.ticker for s in horizon_counts[horizon]]:
                            horizon_counts[horizon].append(signal)

                # Log categorized summary
                logger.info("\n📊 Signals by Time Horizon:")
                if horizon_counts[TimeHorizon.SHORT_TERM]:
                    tickers = [s.ticker for s in horizon_counts[TimeHorizon.SHORT_TERM]]
                    logger.info(f"  ⚡ Short-Term (1-5 days): {len(tickers)} - {', '.join(tickers)}")
                if horizon_counts[TimeHorizon.SWING_TRADE]:
                    tickers = [s.ticker for s in horizon_counts[TimeHorizon.SWING_TRADE]]
                    logger.info(f"  🌊 Swing Trade (1-4 weeks): {len(tickers)} - {', '.join(tickers)}")
                if horizon_counts[TimeHorizon.LONG_TERM]:
                    tickers = [s.ticker for s in horizon_counts[TimeHorizon.LONG_TERM]]
                    logger.info(f"  🏔️  Long-Term (3-12 months): {len(tickers)} - {', '.join(tickers)}")
                logger.info("")

                for signal in signals:
                    self._send_alert(signal)
            else:
                logger.info("\nNo valid signals detected in this scan.")

            # Log statistics
            scan_duration = (datetime.now() - scan_start).total_seconds()
            self._log_statistics(scan_duration)

        except Exception as e:
            logger.error(f"Error during scan job: {e}", exc_info=True)
            self._send_error_notification(str(e))

        logger.info("=" * 60)

    def _send_alert(self, signal: SniperSignal):
        """
        Send an alert for a valid signal.

        Args:
            signal: The sniper signal to alert
        """
        ticker = signal.ticker

        logger.info(f"\nProcessing alert for {ticker}:")
        logger.info(f"  Method: {signal.strategy_result.method_name}")
        logger.info(f"  Score: {signal.strategy_result.score:.1f}/100")
        logger.info(f"  Price: ${signal.strategy_result.current_price:.2f}")

        # Send to Telegram
        success = self.telegram.send_signal(signal)

        if success:
            self.total_alerts_sent += 1
            logger.info(f"  ✓ Alert sent successfully to Telegram")
        else:
            logger.warning(f"  ✗ Failed to send alert (may be throttled)")

    def _send_error_notification(self, error_message: str):
        """Send error notification to Telegram."""
        try:
            self.telegram.send_error_alert(
                f"Scan job encountered an error:\n\n{error_message}"
            )
        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")

    def _log_statistics(self, last_scan_duration: float):
        """Log current statistics."""
        uptime = datetime.now() - self.start_time
        uptime_hours = uptime.total_seconds() / 3600

        logger.info("\n📊 Statistics:")
        logger.info(f"  Total scans: {self.total_scans}")
        logger.info(f"  Total signals found: {self.total_signals}")
        logger.info(f"  Total alerts sent: {self.total_alerts_sent}")
        logger.info(f"  Last scan duration: {last_scan_duration:.1f}s")
        logger.info(f"  Bot uptime: {uptime_hours:.1f} hours")

    def send_startup_notification(self):
        """Send notification that bot has started."""
        message = (
            f"Stock Sniper Bot started successfully!\n\n"
            f"📊 Monitoring {len(self.watchlist)} stocks\n"
            f"⏰ Scanning every {settings.SCAN_INTERVAL_MINUTES} minutes\n"
            f"🛡️ Alert cooldown: {settings.ALERT_COOLDOWN_DAYS} days\n\n"
            f"First scan will run at next scheduled interval."
        )

        try:
            self.telegram.send_status_update(message)
            logger.info("Startup notification sent")
        except Exception as e:
            logger.warning(f"Could not send startup notification: {e}")

    def run_once(self):
        """
        Run a single scan immediately (useful for testing).
        """
        logger.info("Running immediate scan (run_once mode)")
        self.scan_job()

    def run_scheduled(self):
        """
        Run the bot with scheduled scans.

        Scans will run every N minutes as configured in settings.
        """
        # Send startup notification
        self.send_startup_notification()

        # Schedule the scan job
        schedule.every(settings.SCAN_INTERVAL_MINUTES).minutes.do(self.scan_job)

        logger.info(f"\n🚀 Bot is running!")
        logger.info(f"Next scan scheduled for {schedule.next_run()}")
        logger.info("Press Ctrl+C to stop\n")

        # Run the scheduler
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Shutdown signal received")
            self._shutdown()

    def _shutdown(self):
        """Perform cleanup on shutdown."""
        uptime = datetime.now() - self.start_time

        logger.info("=" * 60)
        logger.info("Stock Sniper Bot Shutting Down")
        logger.info("=" * 60)
        logger.info(f"Total runtime: {uptime}")
        logger.info(f"Total scans performed: {self.total_scans}")
        logger.info(f"Total signals detected: {self.total_signals}")
        logger.info(f"Total alerts sent: {self.total_alerts_sent}")

        # Send shutdown notification
        try:
            shutdown_message = (
                f"Stock Sniper Bot stopped.\n\n"
                f"Runtime: {uptime}\n"
                f"Scans: {self.total_scans}\n"
                f"Signals: {self.total_signals}\n"
                f"Alerts: {self.total_alerts_sent}"
            )
            self.telegram.send_status_update(shutdown_message)
        except Exception as e:
            logger.warning(f"Could not send shutdown notification: {e}")

        logger.info("Goodbye!")
        logger.info("=" * 60)


def main():
    """
    Main entry point for the Stock Sniper Bot.

    Usage:
        python stock_sniper/main.py              # Run with scheduler
        python stock_sniper/main.py --once       # Run single scan
    """
    import sys

    # Create bot instance
    bot = SniperBot()

    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # Run once mode (for testing)
        bot.run_once()
    else:
        # Normal scheduled mode
        bot.run_scheduled()


if __name__ == '__main__':
    main()
