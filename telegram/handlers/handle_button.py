"""
Callback query handler for inline buttons
"""

from telegram import Update
from telegram.ext import ContextTypes


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callback queries."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    await query.answer()

    # Edit the message to show which button was pressed
    await query.edit_message_text(text=f"You selected: Option {query.data}")
