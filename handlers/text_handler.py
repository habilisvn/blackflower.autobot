import logging
import httpx
from telegram import Update
from telegram.ext import ContextTypes
from pymemcache.client.base import Client as MemcachedClient


logger = logging.getLogger(__name__)


async def handle_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    # make api request to get the response by httpx
    max_retries = 10
    retry_count = 0

    # Get AI agent from memcached, default to huggingface
    memcached_client = MemcachedClient(("localhost", 11211))
    ai_agent = memcached_client.get("ai_agent")
    if ai_agent is None:
        ai_agent = "huggingface"
    else:
        ai_agent = ai_agent.decode("utf-8")

    while retry_count < max_retries:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8000/api/v1/chat/completions",
                    headers={"ai-agent": ai_agent},
                    json={
                        "message": update.message.text,
                    },
                    timeout=30,
                )
            await update.message.reply_text(response.json()["reply"])
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
