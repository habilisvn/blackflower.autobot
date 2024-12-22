from telegram import Update
from telegram.ext import ContextTypes
from pymemcache.client.base import Client as MemcachedClient


async def default(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    # AI agent options:
    # 1. huggingface
    # 2. openai
    error_message = (
        "You input invalid command.\n"
        "Are you looking for this command: /ai [default|openai]?"
    )

    memcached_client = MemcachedClient(("localhost", 11211))

    # Check if message can be split into 2 parts
    if len(update.message.text.split(" ")) != 2:
        await update.message.reply_text(error_message)
        return

    ai_agent = update.message.text.split(" ")[1]
    # Check if the message includes "huggingface" or "openai"
    if ai_agent == "default":
        # Set the agent to huggingface
        memcached_client.set("ai_agent", "huggingface")

        await update.message.reply_text("Switched to Default AI agent...")
    elif ai_agent == "openai":
        memcached_client.set("ai_agent", "openai")

        await update.message.reply_text("Switched to OpenAI AI agent...")
    else:
        await update.message.reply_text(error_message)
