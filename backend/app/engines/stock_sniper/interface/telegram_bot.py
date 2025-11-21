"""
Telegram Bot Interface Module

Handles:
- Formatting SniperSignal objects into Telegram messages
- Sending alerts to configured Telegram chat/thread
- Alert history tracking with 7-day throttling
- JSON-based alert database management
"""

import logging
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

from app.engines.stock_sniper.config import settings
from app.engines.stock_sniper.core.scanner import SniperSignal

logger = logging.getLogger(__name__)


class AlertHistory:
    """
    Manages alert history and throttling logic.

    Prevents sending duplicate alerts for the same ticker within
    the cooldown period (default: 7 days).
    """

    def __init__(self, db_path: str = None):
        """
        Initialize alert history manager.

        Args:
            db_path: Path to JSON database file
        """
        if db_path is None:
            db_path = settings.ALERT_HISTORY_FILE

        self.db_path = Path(db_path)
        self.alerts: Dict[str, List[Dict[str, Any]]] = {}
        self._load_history()

    def _load_history(self):
        """Load alert history from JSON file."""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    self.alerts = data.get('alerts', {})
                    logger.info(f"Loaded {len(self.alerts)} ticker histories from {self.db_path}")
            except Exception as e:
                logger.error(f"Error loading alert history: {e}")
                self.alerts = {}
        else:
            logger.info(f"No existing alert history found at {self.db_path}")
            self.alerts = {}

    def _save_history(self):
        """Save alert history to JSON file."""
        try:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.db_path, 'w') as f:
                json.dump({
                    'alerts': self.alerts,
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)

            logger.debug(f"Saved alert history to {self.db_path}")
        except Exception as e:
            logger.error(f"Error saving alert history: {e}")

    def can_alert(self, ticker: str) -> bool:
        """
        Check if we can send an alert for this ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            True if cooldown period has passed, False otherwise
        """
        if ticker not in self.alerts:
            return True

        # Get most recent alert
        ticker_history = self.alerts[ticker]
        if not ticker_history:
            return True

        last_alert = ticker_history[-1]
        last_alert_time = datetime.fromisoformat(last_alert['timestamp'])

        # Check if cooldown period has passed
        cooldown_delta = timedelta(days=settings.ALERT_COOLDOWN_DAYS)
        time_since_alert = datetime.now() - last_alert_time

        can_send = time_since_alert >= cooldown_delta

        if not can_send:
            days_remaining = (cooldown_delta - time_since_alert).days
            logger.info(
                f"{ticker}: Throttled - last alert {time_since_alert.days} days ago, "
                f"{days_remaining} days remaining"
            )

        return can_send

    def record_alert(self, ticker: str, signal: SniperSignal):
        """
        Record an alert in the history.

        Args:
            ticker: Stock ticker symbol
            signal: The SniperSignal that was sent
        """
        if ticker not in self.alerts:
            self.alerts[ticker] = []

        alert_record = {
            'timestamp': datetime.now().isoformat(),
            'method': signal.strategy_result.method_name,
            'score': signal.strategy_result.score,
            'price': signal.strategy_result.current_price,
            'target': signal.strategy_result.target_price
        }

        self.alerts[ticker].append(alert_record)
        self._save_history()

        logger.info(f"{ticker}: Alert recorded in history")

    def get_ticker_history(self, ticker: str) -> List[Dict[str, Any]]:
        """Get alert history for a specific ticker."""
        return self.alerts.get(ticker, [])

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about alert history."""
        total_alerts = sum(len(history) for history in self.alerts.values())
        tickers_alerted = len(self.alerts)

        return {
            'total_alerts': total_alerts,
            'unique_tickers': tickers_alerted,
            'tickers': list(self.alerts.keys())
        }


class TelegramBot:
    """
    Telegram bot interface for sending sniper alerts.

    Uses Telegram Bot API via requests library.
    """

    def __init__(self):
        """Initialize Telegram bot."""
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.thread_id = settings.TELEGRAM_THREAD_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.alert_history = AlertHistory()

        # Validate configuration
        if not self.token or self.token == 'your_bot_token_here':
            logger.warning("Telegram bot token not configured!")

        if not self.chat_id:
            logger.warning("Telegram chat ID not configured!")

    def format_signal(self, signal: SniperSignal) -> str:
        """
        Format a SniperSignal into a Telegram message.

        Args:
            signal: The sniper signal to format

        Returns:
            Formatted message string with HTML formatting
        """
        lines = []

        # Header
        lines.append("🎯 <b>SNIPER ALERT: UNDERVALUED STOCK DETECTED</b>")
        lines.append("=" * 50)
        lines.append("")

        # Ticker
        lines.append(f"📊 <b>Ticker:</b> {signal.ticker}")
        lines.append(f"⏰ <b>Time:</b> {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Time Horizons (show all available)
        if len(signal.categorized_strategies) > 0:
            lines.append("⏱️ <b>TIME HORIZONS AVAILABLE:</b>")

            # Sort by time horizon order (short, swing, long)
            from app.engines.stock_sniper.core.strategies import TimeHorizon
            horizon_order = [TimeHorizon.SHORT_TERM, TimeHorizon.SWING_TRADE, TimeHorizon.LONG_TERM]

            for horizon in horizon_order:
                if horizon in signal.categorized_strategies:
                    strat = signal.categorized_strategies[horizon]

                    # Choose emoji based on time horizon
                    emoji = "⚡" if horizon == TimeHorizon.SHORT_TERM else "🌊" if horizon == TimeHorizon.SWING_TRADE else "🏔️"

                    lines.append(f"\n   {emoji} <b>{horizon.value}</b>")
                    lines.append(f"      Method: {strat.method_name}")
                    lines.append(f"      Score: <b>{strat.score:.1f}/100</b>")
                    lines.append(f"      Current: <b>${strat.current_price:.2f}</b>")

                    if strat.target_price:
                        upside = ((strat.target_price - strat.current_price) / strat.current_price) * 100
                        lines.append(f"      Target: <b>${strat.target_price:.2f}</b> (+{upside:.1f}%)")

            lines.append("")

        # Primary Strategy (highest scoring)
        lines.append(f"⭐ <b>PRIMARY SIGNAL: {signal.strategy_result.method_name}</b>")
        lines.append(f"   • {signal.strategy_result.reason}")
        lines.append("")

        # Trigger
        lines.append(f"📈 <b>TECHNICAL TRIGGER:</b>")
        lines.append(f"   • {signal.trigger_result.reason}")
        lines.append(f"   • Status: <b>{'✅ TRIGGERED' if signal.trigger_result.is_triggered else '⏳ WAITING'}</b>")
        lines.append("")

        # Safety
        lines.append(f"🛡️ <b>SAFETY CHECKS:</b>")
        lines.append(f"   • Market Regime: {'✅ Healthy' if signal.safety_result.market_regime_ok else '⚠️ Bearish'}")

        if signal.safety_result.spy_price and signal.safety_result.spy_sma:
            lines.append(
                f"     (SPY ${signal.safety_result.spy_price:.2f} vs "
                f"200-SMA ${signal.safety_result.spy_sma:.2f})"
            )

        lines.append(f"   • Earnings: {'✅ Safe' if signal.safety_result.no_earnings_trap else '⚠️ Within 3 days'}")

        if signal.safety_result.days_to_earnings is not None:
            lines.append(f"     (Next earnings in {signal.safety_result.days_to_earnings} days)")

        lines.append("")

        # Footer
        lines.append("=" * 50)
        lines.append("⚠️ <i>This is algorithmic analysis. Do your own research.</i>")

        return "\n".join(lines)

    def send_message(self, text: str, disable_preview: bool = True) -> bool:
        """
        Send a message to Telegram chat.

        Args:
            text: Message text (supports HTML formatting)
            disable_preview: Disable link previews

        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            url = f"{self.base_url}/sendMessage"

            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML',
                'disable_web_page_preview': disable_preview
            }

            # Add thread ID if specified
            if self.thread_id:
                payload['message_thread_id'] = self.thread_id

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            result = response.json()

            if result.get('ok'):
                logger.info("Message sent successfully to Telegram")
                return True
            else:
                logger.error(f"Telegram API error: {result}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending message to Telegram: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}", exc_info=True)
            return False

    def send_signal(self, signal: SniperSignal) -> bool:
        """
        Send a sniper signal as a Telegram alert.

        Checks throttling before sending.

        Args:
            signal: The sniper signal to send

        Returns:
            True if alert sent successfully, False otherwise
        """
        ticker = signal.ticker

        # Check if we can send alert (throttling)
        if not self.alert_history.can_alert(ticker):
            logger.info(f"{ticker}: Alert throttled (cooldown not expired)")
            return False

        # Format message
        message = self.format_signal(signal)

        # Send message
        success = self.send_message(message)

        # Record in history if successful
        if success:
            self.alert_history.record_alert(ticker, signal)
            logger.info(f"{ticker}: Alert sent and recorded")

        return success

    def send_status_update(self, message: str) -> bool:
        """
        Send a status update message.

        Args:
            message: Status message to send

        Returns:
            True if sent successfully
        """
        formatted = f"ℹ️ <b>Status Update</b>\n\n{message}"
        return self.send_message(formatted)

    def send_error_alert(self, error_message: str) -> bool:
        """
        Send an error alert.

        Args:
            error_message: Error message to send

        Returns:
            True if sent successfully
        """
        formatted = f"❌ <b>Error Alert</b>\n\n{error_message}"
        return self.send_message(formatted)


# Singleton instance
_telegram_bot = None

def get_telegram_bot() -> TelegramBot:
    """Get or create the global TelegramBot instance."""
    global _telegram_bot
    if _telegram_bot is None:
        _telegram_bot = TelegramBot()
    return _telegram_bot


if __name__ == '__main__':
    # Test the Telegram interface
    logging.basicConfig(level=logging.INFO)

    print("Testing Telegram Bot Interface")
    print("=" * 60)

    # Initialize bot
    bot = get_telegram_bot()

    # Test alert history
    print("\nAlert History Stats:")
    stats = bot.alert_history.get_stats()
    print(f"  Total Alerts: {stats['total_alerts']}")
    print(f"  Unique Tickers: {stats['unique_tickers']}")

    # Test message sending (if configured)
    if bot.token and bot.token != 'your_bot_token_here' and bot.chat_id:
        print("\nSending test message...")
        success = bot.send_status_update("Test message from Stock Sniper Bot")
        print(f"  Result: {'Success ✓' if success else 'Failed ✗'}")
    else:
        print("\n⚠️ Telegram not configured - skipping message test")
        print("  Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env")
