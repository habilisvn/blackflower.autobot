import httpx
import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.converters import convert_to_mp3

logger = logging.getLogger(__name__)


# NOTE: context doesn't include any useful information in any way
# Don't use it
async def handle_voice(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    print(update.message)

    # Download the voice message
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
