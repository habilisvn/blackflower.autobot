from telegram import Update
from telegram.ext import ContextTypes


async def default(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Let it be. I don't care.")
