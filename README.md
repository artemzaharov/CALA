# CALA AI

GraphRAG API built with FastAPI, Neo4j, and local LLMs via LM Studio.

Ingest text → extract entities and relations → store in a knowledge graph → query with natural language.

## Stack

- **FastAPI** — API framework
- **Neo4j** — graph database for storing entities and relations
- **LM Studio** — local LLM server (chat + embeddings)
- **uv** — package manager

## Requirements

- [LM Studio](https://lmstudio.ai) running locally with:
  - A chat model loaded (e.g. `glm-4.6v-flash`)
  - An embedding model loaded (e.g. `nomic-embed-text-v1.5`)
  - Local server started on port `1234`
- Docker + Docker Compose

## Setup

```bash
uv sync
```

## Run (development)

Starts FastAPI with hot reload and Neo4j:

```bash
docker compose up --build
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/chat` | Chat with conversation history and optional system prompt |
| POST | `/api/v1/ingest` | Extract entities from text and store in Neo4j with embeddings |
| POST | `/api/v1/query` | Query the knowledge graph using natural language |

## Usage

**Ingest text into the knowledge graph:**
```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{"text": "Elon Musk founded Tesla in 2003. Tesla is located in Austin."}'
```

**Query the knowledge graph:**
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Who started that electric car company?"}'
```

**Chat with history:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "My name is Artem"},
      {"role": "assistant", "content": "Nice to meet you, Artem!"},
      {"role": "user", "content": "What is my name?"}
    ]
  }'
```

## Neo4j Browser

Visual graph explorer available at `http://localhost:7474` (login: `neo4j` / `password`).

```cypher
MATCH (a:Entity)-[r]->(b:Entity) RETURN a, r, b
```

## Code Quality

```bash
docker compose exec api uv run ruff check .
docker compose exec api uv run ruff format .
```

## Tests

```bash
docker compose exec api uv run pytest
```
