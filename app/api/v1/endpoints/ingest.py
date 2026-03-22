import json

from fastapi import APIRouter, HTTPException

from app.core.db import driver
from app.core.llm import CHAT_MODEL, EMBEDDING_MODEL, client
from app.core.prompts import INGEST_SYSTEM_PROMPT
from app.schemas.ingest import ExtractedGraph, IngestRequest, IngestResponse

router = APIRouter()


async def _extract_graph(text: str) -> ExtractedGraph:
    """Send text to LLM and parse the returned JSON into an ExtractedGraph."""
    response = await client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": INGEST_SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
    )

    raw = response.choices[0].message.content

    try:
        # LLM returns a JSON string — parse it and validate with Pydantic.
        # "from" is a reserved keyword in Python so the prompt uses "from",
        # but our schema uses "from_" — we rename it manually before parsing.
        data = json.loads(raw)
        for rel in data.get("relations", []):
            if "from" in rel:
                rel["from_"] = rel.pop("from")
        return ExtractedGraph(**data)
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=422, detail=f"LLM returned invalid JSON: {e}")


async def _get_embedding(text: str) -> list[float]:
    """Convert text into a vector using the embedding model."""
    response = await client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


async def _ensure_vector_index(session) -> None:
    """Create the Neo4j vector index if it doesn't exist yet.

    The index allows fast similarity search over node embeddings.
    dimensions=768 matches nomic-embed-text output size.
    """
    await session.run(
        "CREATE VECTOR INDEX node_embeddings IF NOT EXISTS "
        "FOR (n:Entity) ON (n.embedding) "
        "OPTIONS {indexConfig: {"
        "  `vector.dimensions`: 768,"
        "  `vector.similarity_function`: 'cosine'"
        "}}"
    )


async def _save_to_neo4j(graph: ExtractedGraph) -> tuple[int, int]:
    """Write extracted nodes and relations into Neo4j and return counts."""
    async with driver.session() as session:
        await _ensure_vector_index(session)

        nodes_created = 0
        relations_created = 0

        for node in graph.nodes:
            # Generate embedding for the node — combines name and type for richer meaning.
            # e.g. "Elon Musk Person" captures more context than just "Elon Musk".
            embedding = await _get_embedding(f"{node.name} {node.type}")

            # MERGE prevents duplicates. ON CREATE only runs when node is new.
            # ON MATCH updates the embedding in case the model changed.
            result = await session.run(
                "MERGE (n:Entity {name: $name, type: $type}) "
                "ON CREATE SET n.created = timestamp(), n.embedding = $embedding "
                "ON MATCH SET n.embedding = $embedding "
                "RETURN n",
                name=node.name,
                type=node.type,
                embedding=embedding,
            )
            summary = await result.consume()
            nodes_created += summary.counters.nodes_created

        # MERGE on relationships also prevents duplicate edges.
        for rel in graph.relations:
            result = await session.run(
                "MATCH (a:Entity {name: $from_}), (b:Entity {name: $to}) "
                "MERGE (a)-[r:" + rel.type + "]->(b) "  # noqa: S608
                "RETURN r",
                from_=rel.from_,
                to=rel.to,
            )
            summary = await result.consume()
            relations_created += summary.counters.relationships_created

        return nodes_created, relations_created


@router.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest) -> IngestResponse:
    graph = await _extract_graph(request.text)
    nodes_created, relations_created = await _save_to_neo4j(graph)
    return IngestResponse(nodes_created=nodes_created, relations_created=relations_created)
