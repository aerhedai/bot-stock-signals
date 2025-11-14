"""
Inline button example handler
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with inline keyboard buttons."""
    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data='1'),
            InlineKeyboardButton("Option 2", callback_data='2'),
        ],
        [InlineKeyboardButton("Option 3", callback_data='3')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        'Please choose an option:',
        reply_markup=reply_markup
    )
