"""
Crypto Sniper Bot - Main Entry Point

Orchestrates the complete crypto monitoring pipeline:
1. Loads configuration and crypto watchlist
2. Initializes monitor and Telegram bot
3. Runs scheduled scans every N minutes
4. Sends alerts for detected signals

Run with: python crypto_sniper/main.py
"""

import logging
import time
import schedule
from datetime import datetime
from pathlib import Path

from app.engines.crypto_sniper.config import settings, CRYPTO_WATCHLIST
from app.engines.crypto_sniper.core import CryptoMonitor
from app.engines.crypto_sniper.interface import CryptoTelegramBot

# Ensure log directory exists
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


class CryptoSniperBot:
    """
    Main bot orchestrator that runs scheduled scans and sends alerts.
    """

    def __init__(self):
        """Initialize the crypto sniper bot."""
        logger.info("=" * 60)
        logger.info("Initializing Crypto Sniper Bot")
        logger.info("=" * 60)

        # Load components
        self.monitor = CryptoMonitor()
        self.telegram = CryptoTelegramBot()
        self.watchlist = CRYPTO_WATCHLIST

        # Statistics
        self.total_scans = 0
        self.total_signals = 0
        self.total_alerts_sent = 0
        self.start_time = datetime.now()

        logger.info(f"Configuration loaded:")
        logger.info(f"  Watchlist: {len(self.watchlist)} cryptocurrencies")
        logger.info(f"  Scan interval: {settings.SCAN_INTERVAL_MINUTES} minutes")
        logger.info(f"  Alert cooldown: {settings.ALERT_COOLDOWN_MINUTES} minutes")
        logger.info(f"  Price change threshold (1h): {settings.PRICE_CHANGE_THRESHOLD_1H}%")
        logger.info(f"  Price change threshold (24h): {settings.PRICE_CHANGE_THRESHOLD_24H}%")
        logger.info("=" * 60)

        # Test Telegram connection
        if not self.telegram.test_connection():
            logger.warning("Telegram connection test failed - alerts may not work")

    def scan_job(self):
        """
        Execute a complete scan of the crypto watchlist.

        This is the main job that runs on schedule.
        """
        scan_start = datetime.now()
        logger.info("\n" + "=" * 60)
        logger.info(f"Starting scheduled scan #{self.total_scans + 1}")
        logger.info(f"Time: {scan_start.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)

        try:
            # Run scan
            signals = self.monitor.scan_multiple(self.watchlist)

            self.total_scans += 1
            self.total_signals += len(signals)

            # Send alerts for detected signals
            if signals:
                logger.info(f"\n✓ Found {len(signals)} signal(s)!")

                # Group signals by severity
                severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
                for signal in signals:
                    severity_counts[signal.severity] += 1

                # Log summary
                logger.info("\n📊 Signals by Severity:")
                if severity_counts['critical'] > 0:
                    logger.info(f"  🚨 Critical: {severity_counts['critical']}")
                if severity_counts['high'] > 0:
                    logger.info(f"  ⚠️  High: {severity_counts['high']}")
                if severity_counts['medium'] > 0:
                    logger.info(f"  📊 Medium: {severity_counts['medium']}")
                if severity_counts['low'] > 0:
                    logger.info(f"  ℹ️  Low: {severity_counts['low']}")
                logger.info("")

                # Send each signal
                for signal in signals:
                    self._send_alert(signal)
            else:
                logger.info("\nNo signals detected in this scan.")

            # Log statistics
            scan_duration = (datetime.now() - scan_start).total_seconds()
            self._log_statistics(scan_duration)

        except Exception as e:
            logger.error(f"Error during scan job: {e}", exc_info=True)
            self._send_error_notification(str(e))

        logger.info("=" * 60)

    def _send_alert(self, signal):
        """
        Send an alert for a detected signal.

        Args:
            signal: The crypto signal to alert
        """
        logger.info(f"\nProcessing alert for {signal.symbol}:")
        logger.info(f"  Valuation: {signal.valuation_method}")
        logger.info(f"  Trigger: {signal.trigger_type}")
        logger.info(f"  Severity: {signal.severity}")
        logger.info(f"  Price: ${signal.current_price:,.2f}")
        logger.info(f"  Score: {signal.combined_score:.1f}/100")

        # Send to Telegram
        success = self.telegram.send_signal(signal)

        if success:
            self.total_alerts_sent += 1
            logger.info(f"  ✓ Alert sent successfully to Telegram")
        else:
            logger.warning(f"  ✗ Failed to send alert (may be in cooldown)")

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
            f"Crypto Sniper Bot started successfully!\n\n"
            f"📊 Monitoring {len(self.watchlist)} cryptocurrencies\n"
            f"⏰ Scanning every {settings.SCAN_INTERVAL_MINUTES} minutes\n"
            f"🚨 Price change threshold (1h): {settings.PRICE_CHANGE_THRESHOLD_1H}%\n"
            f"📈 Price change threshold (24h): {settings.PRICE_CHANGE_THRESHOLD_24H}%\n\n"
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
        logger.info("Crypto Sniper Bot Shutting Down")
        logger.info("=" * 60)
        logger.info(f"Total runtime: {uptime}")
        logger.info(f"Total scans performed: {self.total_scans}")
        logger.info(f"Total signals detected: {self.total_signals}")
        logger.info(f"Total alerts sent: {self.total_alerts_sent}")

        # Send shutdown notification
        try:
            shutdown_message = (
                f"Crypto Sniper Bot stopped.\n\n"
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
    Main entry point for the Crypto Sniper Bot.

    Usage:
        python crypto_sniper/main.py              # Run with scheduler
        python crypto_sniper/main.py --once       # Run single scan
    """
    import sys

    # Create bot instance
    bot = CryptoSniperBot()

    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # Run once mode (for testing)
        bot.run_once()
    else:
        # Normal scheduled mode
        bot.run_scheduled()


if __name__ == '__main__':
    main()
