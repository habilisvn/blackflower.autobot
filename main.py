#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os
import subprocess
from dotenv import load_dotenv
import httpx
from telegram import ForceReply, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
# set higher logging level for httpx to avoid all GET and POST requests being
# logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def help_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Let it be. I don't care.")


async def handle_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    # make api request to get the response by httpx
    max_retries = 10
    retry_count = 0

    while retry_count < max_retries:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8000/api/v1/chat/completions",
                    json={"message": update.message.text},
                )
            await update.message.reply_text(response.json()["reply"])
            return
        except Exception as e:
            logger.error(
                f"Error making API request "
                f"(attempt {retry_count + 1}/{max_retries}): {e}"
            )
            retry_count += 1

    # If we get here, all retries failed
    logger.error("Failed after all retries")
    await update.message.reply_text(
        "I'm sorry, but I'm having trouble processing your request. "
        "Please try again later."
    )


async def handle_voice(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    voice_file = await update.message.voice.get_file()
    await voice_file.download_to_drive("voice_message.ogg")
    output_file = convert_to_mp3("voice_message.ogg", "voice_message.mp3")

    max_retries = 10
    retry_count = 0

    while retry_count < max_retries:
        try:
            # using httpx to send the mp3 file to the server
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8000/api/v1/chat/transcribe",
                    files={"upload_file": open(output_file, "rb")},
                )

            if "reply" in response.json():
                await update.message.reply_text(response.json()["reply"])
            else:
                await update.message.reply_text(
                    "Sorry, I'm having trouble processing your request. "
                    "Please try again later."
                )

            # Stop handler if success
            return
        except httpx.ReadTimeout as e:
            logger.error(
                f"Error making API request "
                f"(attempt {retry_count + 1}/{max_retries}): {e}"
            )
            retry_count += 1

    # If we get here, all retries failed
    logger.error("Failed after all retries")
    await update.message.reply_text(
        "I'm sorry, but I'm having trouble processing your request. "
        "Please try again later."
    )


def convert_to_mp3(input_file: str, output_file: str):
    # Delete the output file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)

    # Convert the OGG file to MP3 using FFmpeg
    command = [
        "ffmpeg",
        "-i",
        input_file,
        "-acodec",
        "libmp3lame",
        output_file,
    ]
    subprocess.run(command, check=True)
    return output_file


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
    main()
