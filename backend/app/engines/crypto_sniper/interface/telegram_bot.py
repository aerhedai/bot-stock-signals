"""
Telegram Bot Integration for Crypto Sniper

Sends crypto alerts to Telegram channel/group with topic support.
"""

import logging
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict

from app.engines.crypto_sniper.config import settings
from app.engines.crypto_sniper.core.monitor import CryptoSignal

logger = logging.getLogger(__name__)


class CryptoTelegramBot:
    """
    Handles sending crypto alerts to Telegram.
    """

    def __init__(self):
        """Initialize the Telegram bot."""
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.thread_id = settings.TELEGRAM_THREAD_ID

        # Alert history for cooldown management
        self.alert_history: Dict[str, datetime] = {}
        self.load_alert_history()

        logger.info("CryptoTelegramBot initialized")

    def load_alert_history(self):
        """Load alert history from file."""
        try:
            history_file = Path(settings.ALERT_HISTORY_FILE)
            if history_file.exists():
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    # Convert timestamps back to datetime
                    self.alert_history = {
                        symbol: datetime.fromisoformat(timestamp)
                        for symbol, timestamp in data.items()
                    }
                logger.info(f"Loaded {len(self.alert_history)} alert history entries")
        except Exception as e:
            logger.warning(f"Could not load alert history: {e}")
            self.alert_history = {}

    def save_alert_history(self):
        """Save alert history to file."""
        try:
            history_file = Path(settings.ALERT_HISTORY_FILE)
            history_file.parent.mkdir(parents=True, exist_ok=True)

            # Convert datetime to ISO format strings
            data = {
                symbol: timestamp.isoformat()
                for symbol, timestamp in self.alert_history.items()
            }

            with open(history_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Could not save alert history: {e}")

    def can_send_alert(self, symbol: str) -> bool:
        """
        Check if enough time has passed since last alert for this symbol.

        Args:
            symbol: Crypto symbol

        Returns:
            True if alert can be sent
        """
        if symbol not in self.alert_history:
            return True

        last_alert = self.alert_history[symbol]
        cooldown_period = timedelta(minutes=settings.ALERT_COOLDOWN_MINUTES)

        return datetime.now() - last_alert >= cooldown_period

    def record_alert(self, symbol: str):
        """Record that an alert was sent for this symbol."""
        self.alert_history[symbol] = datetime.now()
        self.save_alert_history()

    def format_signal(self, signal: CryptoSignal) -> str:
        """
        Format a crypto signal as a Telegram message with valuation and technical data.

        Args:
            signal: The crypto signal to format

        Returns:
            Formatted message string
        """
        # Severity emoji
        severity_emoji = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': '📊',
            'low': 'ℹ️'
        }
        emoji = severity_emoji.get(signal.severity, '📊')

        # Build message header
        lines = [
            f"{emoji} <b>{signal.name} ({signal.symbol})</b> - {signal.severity.upper()}",
            f"",
            f"💰 <b>Price:</b> ${signal.current_price:,.4f}",
        ]

        # ==================================================
        # VALUATION LAYER
        # ==================================================
        lines.append("")
        lines.append("📈 <b>VALUATION</b>")

        # Valuation method and score
        lines.append(f"<b>Method:</b> {signal.valuation_method}")
        lines.append(f"<b>Score:</b> {signal.valuation_score:.0f}/100")

        # Fair value and discount
        if signal.fair_value_estimate:
            lines.append(f"<b>Fair Value:</b> ${signal.fair_value_estimate:,.4f}")

        if signal.discount_percentage:
            lines.append(f"<b>Discount:</b> {signal.discount_percentage:.1f}% undervalued")

        # ==================================================
        # TECHNICAL TRIGGER
        # ==================================================
        lines.append("")
        lines.append("🎯 <b>ENTRY TRIGGER</b>")
        lines.append(f"<b>Signal:</b> {signal.trigger_description}")

        # Technical indicators
        if signal.rsi is not None:
            rsi_status = "Oversold" if signal.rsi < 30 else "Overbought" if signal.rsi > 70 else "Neutral"
            lines.append(f"<b>RSI:</b> {signal.rsi:.1f} ({rsi_status})")

        if signal.macd:
            macd_signal = "Bullish ✅" if signal.macd['histogram'] > 0 else "Bearish ❌"
            lines.append(f"<b>MACD:</b> {macd_signal}")

        if signal.bollinger_position:
            bb_desc = {
                'above_upper': 'Above upper (overbought)',
                'below_lower': 'Below lower (oversold)',
                'within_bands': 'Within bands'
            }
            lines.append(f"<b>BB:</b> {bb_desc.get(signal.bollinger_position, 'Unknown')}")

        # ==================================================
        # PRICE PERFORMANCE
        # ==================================================
        lines.append("")
        lines.append("📊 <b>PERFORMANCE</b>")

        # Price changes (now using daily data)
        if signal.change_1h is not None:  # Actually 1d
            change_emoji = '🟢' if signal.change_1h > 0 else '🔴'
            lines.append(f"<b>1 Day:</b> {change_emoji} {signal.change_1h:+.2f}%")

        if signal.change_24h is not None:  # Actually 7d
            change_emoji = '🟢' if signal.change_24h > 0 else '🔴'
            lines.append(f"<b>7 Days:</b> {change_emoji} {signal.change_24h:+.2f}%")

        if signal.change_7d is not None:  # Actually 30d
            change_emoji = '🟢' if signal.change_7d > 0 else '🔴'
            lines.append(f"<b>30 Days:</b> {change_emoji} {signal.change_7d:+.2f}%")

        if signal.volume_change is not None:
            vol_emoji = '💥' if signal.volume_change > 100 else '📊'
            lines.append(f"<b>Volume:</b> {vol_emoji} {signal.volume_change:+.0f}% vs avg")

        # ==================================================
        # METADATA
        # ==================================================
        lines.append("")
        lines.append(f"<b>Score:</b> {signal.combined_score:.0f}/100")
        lines.append(f"<b>Category:</b> {signal.category}")
        lines.append(f"<b>Confidence:</b> {signal.confidence.title()}")
        lines.append(f"<b>Time:</b> {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

        return "\n".join(lines)

    def send_message(self, text: str, parse_mode: str = 'HTML') -> bool:
        """
        Send a message to Telegram.

        Args:
            text: Message text
            parse_mode: Parse mode (HTML or Markdown)

        Returns:
            True if successful
        """
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }

            # Add thread ID if configured (for topic-based groups)
            if self.thread_id:
                payload['message_thread_id'] = int(self.thread_id)

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            logger.debug("Message sent successfully")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    def send_signal(self, signal: CryptoSignal) -> bool:
        """
        Send a crypto signal alert to Telegram.

        Args:
            signal: The crypto signal to send

        Returns:
            True if successful
        """
        # Check cooldown
        if not self.can_send_alert(signal.symbol):
            logger.info(f"Alert for {signal.symbol} in cooldown period, skipping")
            return False

        # Format and send message
        message = self.format_signal(signal)
        success = self.send_message(message)

        if success:
            self.record_alert(signal.symbol)
            logger.info(f"Alert sent for {signal.symbol}: {signal.trigger_type}")

        return success

    def send_status_update(self, message: str) -> bool:
        """
        Send a status update message.

        Args:
            message: Status message text

        Returns:
            True if successful
        """
        return self.send_message(f"ℹ️ <b>Crypto Sniper Status</b>\n\n{message}")

    def send_error_alert(self, error_message: str) -> bool:
        """
        Send an error alert.

        Args:
            error_message: Error message text

        Returns:
            True if successful
        """
        return self.send_message(f"❌ <b>Crypto Sniper Error</b>\n\n{error_message}")

    def test_connection(self) -> bool:
        """
        Test Telegram bot connection.

        Returns:
            True if connection successful
        """
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            bot_info = response.json()
            if bot_info.get('ok'):
                username = bot_info.get('result', {}).get('username', 'Unknown')
                logger.info(f"Telegram bot connected: @{username}")
                return True

            return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False
