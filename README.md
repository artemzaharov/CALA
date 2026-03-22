# CALA AI

Minimal FastAPI starter.

## Setup

```bash
uv sync
```

## Run API

```bash
uv run uvicorn app.main:app --reload
```

## Code Quality

```bash
uv run ruff check .
uv run ruff format .
```

## Docker

```bash
docker build -t cala-ai .
docker run --rm -p 8000:8000 cala-ai
```

## Open

- http://127.0.0.1:8000/api/v1/health
- http://127.0.0.1:8000/docs
