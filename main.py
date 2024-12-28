import logging
import os
from time import time
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)
from telegram.error import TelegramError, TimedOut, NetworkError

from commands.help_command import default as help_command
from commands.switch_ai_command import default as switch_ai_command
from handlers.text_handler import handle_text
from handlers.voice_handler import handle_voice

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
# set higher logging level for httpx to avoid all GET and POST requests being
# logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main() -> None:
    load_dotenv()

    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = (
        Application.builder()
        .token(os.getenv("TELEGRAM_BOT_TOKEN"))
        .concurrent_updates(True)
        .build()
    )

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ai", switch_ai_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )
    application.add_handler(
        MessageHandler(filters.VOICE & ~filters.COMMAND, handle_voice)
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    previous_error_time = time()
    error_count = 0

    while True:
        try:
            main()
        except (TelegramError, TimedOut, NetworkError) as e:
            logger.error(f"An error occurred: {e}")

            if time() - previous_error_time < 600:
                # Increase the sleep time 5 seconds for each error
                time.sleep(5 + error_count * 5)
            else:
                # Reset if the error is the first error in 10 minutes
                time.sleep(5)
                error_count = 0

            previous_error_time = time()
            error_count += 1
