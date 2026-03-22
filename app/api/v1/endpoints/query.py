from fastapi import APIRouter

from app.core.db import driver
from app.core.llm import client
from app.core.prompts import QUERY_SYSTEM_PROMPT
from app.schemas.query import QueryRequest, QueryResponse

router = APIRouter()


async def _fetch_context(question: str) -> list[str]:
    """Search the graph for nodes and relations relevant to the question.

    Strategy: find all nodes whose name appears in the question,
    then return all their direct relationships as plain text sentences.
    """
    async with driver.session() as session:
        result = await session.run(
            # For each node whose name is mentioned in the question,
            # collect all its outgoing relationships and connected nodes.
            "MATCH (n)-[r]->(m) "
            "WHERE toLower($question) CONTAINS toLower(n.name) "
            "   OR toLower($question) CONTAINS toLower(m.name) "
            "RETURN n.name AS from_, type(r) AS rel, m.name AS to",
            question=question,
        )
        records = await result.data()

    # Convert each row into a readable sentence the LLM can understand.
    # e.g. "Elon Musk FOUNDED Tesla"
    context = [f"{r['from_']} {r['rel']} {r['to']}" for r in records]
    return context


async def _generate_answer(question: str, context: list[str]) -> str:
    """Send the question and graph context to the LLM and return its answer."""
    if not context:
        return "I don't know — no relevant information found in the knowledge graph."

    # Format context as a numbered list so the LLM can reference it clearly.
    context_text = "\n".join(f"- {c}" for c in context)

    response = await client.chat.completions.create(
        model="local-model",
        messages=[
            {"role": "system", "content": QUERY_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context from knowledge graph:\n{context_text}\n\nQuestion: {question}",
            },
        ],
    )

    return response.choices[0].message.content


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    context = await _fetch_context(request.question)
    answer = await _generate_answer(request.question, context)
    return QueryResponse(answer=answer, context=context)
