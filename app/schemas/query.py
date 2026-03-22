from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    # Raw context pulled from Neo4j — useful for debugging what the LLM saw.
    context: list[str]
