from pydantic import BaseModel


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
