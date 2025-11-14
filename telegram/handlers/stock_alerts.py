"""
Stock Alert Handler
Handles sending stock price alerts to the configured Telegram group.
"""

from telegram import Bot
from telegram.constants import ParseMode
from config import Config
import logging

logger = logging.getLogger(__name__)


def format_stock_alert(
    ticker: str,
    current_price: float,
    target_price: float,
    change_percent: float,
    alert_type: str = "UNDERPRICED",
    additional_info: dict = None
) -> str:
    """
    Format a stock alert message with nice formatting.

    Args:
        ticker: Stock ticker symbol
        current_price: Current stock price
        target_price: Target/fair value price
        change_percent: Percentage change
        alert_type: Type of alert (UNDERPRICED, OVERPRICED, etc.)
        additional_info: Additional data to include (volume, market_cap, etc.)

    Returns:
        Formatted message string with HTML formatting
    """
    # Determine emoji based on alert type
    emoji = "📉" if alert_type == "UNDERPRICED" else "📈"

    # Build the message
    message = f"{emoji} <b>{alert_type} ALERT</b> {emoji}\n\n"
    message += f"<b>Ticker:</b> ${ticker}\n"
    message += f"<b>Current Price:</b> ${current_price:.2f}\n"
    message += f"<b>Target Price:</b> ${target_price:.2f}\n"
    message += f"<b>Difference:</b> {change_percent:+.2f}%\n"

    # Calculate potential gain/loss
    potential = ((target_price - current_price) / current_price) * 100
    if potential > 0:
        message += f"<b>Upside Potential:</b> +{potential:.2f}% 🚀\n"
    else:
        message += f"<b>Downside Risk:</b> {potential:.2f}% ⚠️\n"

    # Add additional info if provided
    if additional_info:
        message += "\n<b>Additional Info:</b>\n"
        for key, value in additional_info.items():
            message += f"  • {key}: {value}\n"

    return message


async def send_stock_alert(
    bot: Bot,
    message_thread_id: int,
    ticker: str,
    current_price: float,
    target_price: float,
    change_percent: float,
    alert_type: str = "UNDERPRICED",
    additional_info: dict = None
) -> bool:
    """
    Send a stock alert to the configured group chat in a specific topic.

    Args:
        bot: Telegram Bot instance
        message_thread_id: Topic/thread ID to send the message to
        ticker: Stock ticker symbol
        current_price: Current stock price
        target_price: Target/fair value price
        change_percent: Percentage change
        alert_type: Type of alert
        additional_info: Additional data to include

    Returns:
        True if message was sent successfully, False otherwise
    """
    if not Config.GROUP_CHAT_ID:
        logger.error("GROUP_CHAT_ID not configured. Cannot send alert.")
        return False

    try:
        message = format_stock_alert(
            ticker=ticker,
            current_price=current_price,
            target_price=target_price,
            change_percent=change_percent,
            alert_type=alert_type,
            additional_info=additional_info
        )

        await bot.send_message(
            chat_id=Config.GROUP_CHAT_ID,
            message_thread_id=message_thread_id,
            text=message,
            parse_mode=ParseMode.HTML
        )

        logger.info(f"Successfully sent {alert_type} alert for {ticker} to topic {message_thread_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to send stock alert: {e}", exc_info=True)
        return False


async def send_custom_alert(bot: Bot, message_thread_id: int, message: str) -> bool:
    """
    Send a custom formatted message to the group chat in a specific topic.

    Args:
        bot: Telegram Bot instance
        message_thread_id: Topic/thread ID to send the message to
        message: Custom message to send (supports HTML formatting)

    Returns:
        True if message was sent successfully, False otherwise
    """
    if not Config.GROUP_CHAT_ID:
        logger.error("GROUP_CHAT_ID not configured. Cannot send alert.")
        return False

    try:
        await bot.send_message(
            chat_id=Config.GROUP_CHAT_ID,
            message_thread_id=message_thread_id,
            text=message,
            parse_mode=ParseMode.HTML
        )

        logger.info(f"Successfully sent custom alert to topic {message_thread_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to send custom alert: {e}", exc_info=True)
        return False
