from fastapi import APIRouter

from app.core.db import driver
from app.core.llm import CHAT_MODEL, EMBEDDING_MODEL, client
from app.core.prompts import QUERY_SYSTEM_PROMPT
from app.schemas.query import QueryRequest, QueryResponse

router = APIRouter()


async def _fetch_context(question: str) -> list[str]:
    """Search the graph for nodes relevant to the question using vector similarity.

    Strategy:
    1. Convert the question into a vector (embedding).
    2. Find the 5 most semantically similar nodes in Neo4j.
    3. Return all their direct relationships as plain text sentences.
    """
    # Convert the question into a vector so we can compare it against node embeddings.
    response = await client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=question,
    )
    question_vector = response.data[0].embedding

    async with driver.session() as session:
        result = await session.run(
            # queryNodes finds the top-k nodes whose embedding is closest to the question vector.
            # cosine similarity — angle between vectors, 1.0 = identical meaning, 0.0 = unrelated.
            # Then we follow all outgoing relationships from those nodes to build context.
            "CALL db.index.vector.queryNodes('node_embeddings', 5, $vector) "
            "YIELD node, score "
            "MATCH (a:Entity)-[r]->(b:Entity) "
            "WHERE a = node OR b = node "
            "RETURN a.name AS from_, type(r) AS rel, b.name AS to, score "
            "ORDER BY score DESC",
            vector=question_vector,
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

    # Format context as a bullet list so the LLM can reference it clearly.
    context_text = "\n".join(f"- {c}" for c in context)

    response = await client.chat.completions.create(
        model=CHAT_MODEL,
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
