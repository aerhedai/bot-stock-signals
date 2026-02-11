"""
Main Telegram Bot Application
This is the entry point for your Telegram bot.
"""

import logging
import sys
from pathlib import Path

# Ensure telegram/ directory is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from config import Config
from handlers import start, help_command, echo, button, handle_button, stock_alerts

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL)
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)


async def test_alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a test stock alert to the configured group chat topic."""
    # Check if user is admin
    if update.effective_user.id not in Config.ADMIN_IDS and Config.ADMIN_IDS:
        await update.message.reply_text("⚠️ You don't have permission to use this command.")
        return

    # Check if DEFAULT_MESSAGE_THREAD_ID is configured
    if not Config.DEFAULT_MESSAGE_THREAD_ID:
        await update.message.reply_text(
            "❌ DEFAULT_MESSAGE_THREAD_ID not configured in .env file.\n\n"
            "To get your topic ID:\n"
            "1. Use /gettopicid command in your topic\n"
            "2. Or visit: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates"
        )
        return

    # Send a test alert
    success = await stock_alerts.send_stock_alert(
        bot=context.bot,
        message_thread_id=Config.DEFAULT_MESSAGE_THREAD_ID,
        ticker="AAPL",
        current_price=150.25,
        target_price=180.00,
        change_percent=-16.53,
        alert_type="UNDERPRICED",
        additional_info={
            "Volume": "52.3M",
            "Market Cap": "$2.45T",
            "P/E Ratio": "25.4"
        }
    )

    if success:
        await update.message.reply_text(
            f"✅ Test alert sent successfully to topic {Config.DEFAULT_MESSAGE_THREAD_ID}!"
        )
    else:
        await update.message.reply_text(
            "❌ Failed to send alert. Check logs, GROUP_CHAT_ID, and DEFAULT_MESSAGE_THREAD_ID configuration."
        )


async def get_admin_ids(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get all admin user IDs from the current group chat."""
    # Check if this is a group message
    if update.message.chat.type not in ['group', 'supergroup']:
        await update.message.reply_text(
            "⚠️ This command only works in group chats.\n"
            "Please use it inside your group."
        )
        return

    try:
        # Get chat administrators
        chat_id = update.message.chat.id
        admins = await context.bot.get_chat_administrators(chat_id)

        # Build response message
        message = f"👥 <b>Group Administrators</b>\n\n"
        message += f"<b>Group ID:</b> <code>{chat_id}</code>\n"
        message += f"<b>Total Admins:</b> {len(admins)}\n\n"

        admin_ids = []
        for admin in admins:
            user = admin.user
            admin_ids.append(str(user.id))

            # Build admin info
            name = user.full_name or user.first_name or "Unknown"
            username = f"@{user.username}" if user.username else "No username"
            status = "👑 Owner" if admin.status == "creator" else "🛡️ Admin"

            message += f"{status} <b>{name}</b>\n"
            message += f"  • ID: <code>{user.id}</code>\n"
            message += f"  • Username: {username}\n"
            if user.is_bot:
                message += f"  • 🤖 Bot\n"
            message += "\n"

        # Add helpful info for .env
        message += f"<b>For .env file:</b>\n"
        message += f"<code>ADMIN_IDS={','.join(admin_ids)}</code>"

        await update.message.reply_text(message, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Error getting admin IDs: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Error getting administrators: {str(e)}\n\n"
            "Make sure the bot has permission to view group members."
        )


async def get_topic_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get the topic/thread ID of the current chat."""
    # Check if this is a group message
    if update.message.chat.type not in ['group', 'supergroup']:
        await update.message.reply_text(
            "⚠️ This command only works in group chats.\n"
            "Please use it inside a topic in your group."
        )
        return

    # Get the message thread ID
    thread_id = update.message.message_thread_id

    if thread_id:
        # Reply in the same topic by using message_thread_id
        await context.bot.send_message(
            chat_id=update.message.chat.id,
            message_thread_id=thread_id,
            text=f"📋 <b>Topic Information</b>\n\n"
                 f"<b>Topic ID:</b> <code>{thread_id}</code>\n"
                 f"<b>Group ID:</b> <code>{update.message.chat.id}</code>\n\n"
                 f"Use this topic ID in your .env file:\n"
                 f"<code>STOCK_NEWS_TOPIC_ID={thread_id}</code>\n"
                 f"<code>CRYPTO_NEWS_TOPIC_ID={thread_id}</code>\n\n"
                 f"Or in your algorithm:\n"
                 f"<code>send_alert_sync(\n"
                 f"    message_thread_id={thread_id},\n"
                 f"    ticker=\"AAPL\",\n"
                 f"    ...\n"
                 f")</code>",
            parse_mode=ParseMode.HTML
        )
    else:
        # General chat (no topic)
        await update.message.reply_text(
            "ℹ️ This appears to be the general chat (no topic).\n\n"
            f"<b>Group ID:</b> <code>{update.message.chat.id}</code>\n\n"
            "If you want to send messages to a specific topic:\n"
            "1. Create topics in your group (enable forum mode)\n"
            "2. Use this command inside a topic to get its ID",
            parse_mode=ParseMode.HTML
        )


def main() -> None:
    """Start the bot."""
    # Validate configuration
    Config.validate()

    # Create the Application
    application = Application.builder().token(Config.BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start.start))
    application.add_handler(CommandHandler("help", help_command.help_command))
    application.add_handler(CommandHandler("button", button.button))
    application.add_handler(CommandHandler("testalert", test_alert))
    application.add_handler(CommandHandler("getadminids", get_admin_ids))
    application.add_handler(CommandHandler("gettopicid", get_topic_id))

    # Register callback query handler for inline buttons
    application.add_handler(CallbackQueryHandler(handle_button.handle_button))

    # Register message handler for echoing text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo.echo))

    # Register error handler
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
