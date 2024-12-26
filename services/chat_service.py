from dataclasses import dataclass
import httpx
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()


@dataclass
class ChatHeaders:
    ai_agent: str


def get_api_url(feature: str):
    return (
        f"{os.getenv('API_HOST')}"
        f":{os.getenv('API_PORT')}"
        f"{os.getenv('API_PREFIX')}"
        f"/{feature}"
    )


async def completions(
    *, message: str, timeout: int = 30, ai_agent: str = "openai"
):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            get_api_url("completions"),
            headers={"ai-gent": ai_agent},
            json={"message": message},
            timeout=timeout,
        )
    return response.json()["reply"]


async def transcribe(file_path: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            get_api_url("transcribe"),
            files={"upload_file": open(file_path, "rb")},
        )
    if "reply" in response.json():
        return response.json()["reply"]
    else:
        return (
            "Sorry, I'm having trouble processing your request. "
            "Please try again later."
        )
