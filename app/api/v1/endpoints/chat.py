from fastapi import APIRouter

from app.core.llm import client
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


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
