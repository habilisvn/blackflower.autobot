import logging
from telegram import Update
from telegram.ext import ContextTypes
from pymemcache.client.base import Client as MemcachedClient

from services.chat_service import completions


logger = logging.getLogger(__name__)


async def handle_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    # make api request to get the response by httpx
    max_retries = 10
    retry_count = 0

    # Get AI agent from memcached, default to huggingface
    memcached_client = MemcachedClient(("localhost", 11211))
    ai_agent = memcached_client.get("ai_agent", "openai")

    # Terminate if the count of retries is greater than max_retries
    while retry_count < max_retries:
        try:
            response = await completions(
                message=update.message.text, ai_agent=ai_agent
            )
            await update.message.reply_text(response)

            # Return after successful response
            return
        except Exception as e:
            logger.error(update.message)
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
