"""
/help command handler
"""

from telegram import Update
from telegram.ext import ContextTypes


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "Available commands:\n\n"
        "/start - Start the bot and get a welcome message\n"
        "/help - Show this help message\n"
        "/button - Show an example inline keyboard\n\n"
    )
    await update.message.reply_text(help_text)
