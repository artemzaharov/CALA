import os

from openai import AsyncOpenAI

# Read LM Studio base URL from environment variable.
# This allows different values in local dev, Docker, and production
# without changing the code — just set LM_STUDIO_URL in the environment.
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://host.docker.internal:1234/v1")

# AsyncOpenAI makes non-blocking HTTP calls — compatible with async def endpoints.
# The sync OpenAI client would block the event loop on every request.
client = AsyncOpenAI(
    base_url=LM_STUDIO_URL,
    api_key="lm-studio",
)
