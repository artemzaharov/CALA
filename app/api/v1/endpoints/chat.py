from fastapi import APIRouter
from pydantic import BaseModel

from app.core.llm import client

router = APIRouter()


# A single message in the conversation history.
# role can be: "user" (human), "assistant" (model), "system" (model instructions).
class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    # Full conversation history — the client stores it and sends it whole with every request.
    # The server is stateless: it has no memory of previous requests, all state lives in messages.
    messages: list[Message]
    # Optional system prompt — prepended to messages before sending to the model.
    # If not provided, the model behaves as a general-purpose assistant.
    system_prompt: str | None = None


class ChatResponse(BaseModel):
    # The model's reply — the client should append it to its history as {"role": "assistant", ...}
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    # Convert Pydantic models to dicts — the OpenAI client expects that format.
    messages = [m.model_dump() for m in request.messages]

    # If a system prompt is provided, inject it as the first message.
    # The model reads it before anything else — it sets the rules for the whole conversation.
    if request.system_prompt:
        messages = [{"role": "system", "content": request.system_prompt}] + messages

    response = await client.chat.completions.create(
        model="local-model",
        messages=messages,
    )

    reply = response.choices[0].message.content
    return ChatResponse(reply=reply)
