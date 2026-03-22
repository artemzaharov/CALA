import json

from fastapi import APIRouter, HTTPException

from app.core.db import driver
from app.core.llm import client
from app.core.prompts import INGEST_SYSTEM_PROMPT
from app.schemas.ingest import ExtractedGraph, IngestRequest, IngestResponse

router = APIRouter()


async def _extract_graph(text: str) -> ExtractedGraph:
    """Send text to LLM and parse the returned JSON into an ExtractedGraph."""
    response = await client.chat.completions.create(
        model="local-model",
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


async def _save_to_neo4j(graph: ExtractedGraph) -> tuple[int, int]:
    """Write extracted nodes and relations into Neo4j and return counts."""
    async with driver.session() as session:
        nodes_created = 0
        relations_created = 0

        # MERGE means: create the node only if it doesn't already exist.
        # This prevents duplicates when the same entity appears in multiple texts.
        for node in graph.nodes:
            result = await session.run(
                "MERGE (n {name: $name, type: $type}) "
                "ON CREATE SET n.created = timestamp() "
                "RETURN n",
                name=node.name,
                type=node.type,
            )
            summary = await result.consume()
            nodes_created += summary.counters.nodes_created

        # MERGE on relationships also prevents duplicate edges.
        for rel in graph.relations:
            result = await session.run(
                "MATCH (a {name: $from_}), (b {name: $to}) "
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
