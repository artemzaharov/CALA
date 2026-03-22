# CALA AI — Anki Cards

## What is the event loop?

A single-threaded (однопоточный) loop that runs coroutines (корутины). Instead of blocking (блокировать) and waiting, it switches between tasks at every `await` point. FastAPI and uvicorn run on top of it.

## What is the difference between `async def` and `def`?

`async def` defines a coroutine — it can pause at `await` and let the event loop handle other tasks. `def` is a regular function that runs to completion and blocks the thread.

## What does `await` actually do?

Pauses the current coroutine and yields (передаёт) control back to the event loop until the awaited (ожидаемый) operation completes. Only works inside `async def`.

## When should you use `async def` vs `def` in FastAPI?

Use `async def` when the endpoint does I/O (network, database, file). Use `def` for CPU-heavy (вычислительно затратных) work — FastAPI automatically runs it in a threadpool so it doesn't block the event loop.

## What is a coroutine (корутина)?

A function defined with `async def`. Calling it returns a coroutine object — it doesn't run until you `await` it or schedule it in the event loop.

## What blocks the event loop?

Any synchronous (синхронный) operation that takes time without `await`: CPU computation, `time.sleep()`, sync HTTP calls, sync DB queries. While it runs, no other request can be handled.

## What is the difference between ThreadPoolExecutor and ProcessPoolExecutor?

`ThreadPoolExecutor` — multiple threads, still limited by GIL for CPU tasks. `ProcessPoolExecutor` — separate processes with their own GIL, truly parallel (параллельный) for CPU work. Use processes for heavy computation, threads for I/O.

## Why does CPU-bound work block the event loop even with `await`?

`await` only yields when the underlying (нижележащая) function actually pauses — like waiting for a network response. Pure computation never pauses, so the event loop stays frozen until it finishes.

## What is GIL and how does free-threaded Python 3.13 change it?

GIL (Global Interpreter Lock) allows only one thread to execute Python bytecode at a time. In Python 3.13 free-threaded mode (experimental), GIL is removed — threads can run truly in parallel on multiple CPU cores.

## What is APIRouter in FastAPI and why use it?

A mini-router that groups related endpoints. You define routes on it, then include it in the main app with `app.include_router(...)`. Keeps endpoints organized by feature instead of all in one file.

## What is `lifespan` in FastAPI?

An async context manager (менеджер контекста) that runs code on startup (before `yield`) and shutdown (after `yield`). Replaces deprecated `@app.on_event`. Used to open/close DB connections, thread pools, etc.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield  # server is running
    await driver.close()  # shutdown
```

## Where should Pydantic schemas live in a FastAPI project?

In a separate `app/schemas/` directory, one file per domain (e.g. `chat.py`, `ingest.py`). Not inside endpoint files — schemas are reusable and should be independent of routing logic.

## What is `response_model` in FastAPI?

Tells FastAPI which Pydantic model to use for the response. It validates (проверяет) the output, strips (удаляет) extra fields, and generates correct OpenAPI docs.

```python
@router.post("/chat", response_model=ChatResponse)
```

## How does FastAPI handle async vs sync endpoint functions differently?

`async def` endpoints run directly in the event loop. `def` endpoints are automatically run in a threadpool so they don't block other requests.

## How does FastAPI generate OpenAPI docs automatically?

It reads type hints and Pydantic models on all routes and generates a JSON schema. Swagger UI at `/docs` and ReDoc at `/redoc` render it interactively.

## What is `model_dump()` in Pydantic v2?

Converts a Pydantic model instance to a plain Python dict. Used when an external library (like OpenAI client) expects a dict, not a Pydantic object.

```python
messages = [m.model_dump() for m in request.messages]
```

## What is dependency injection (внедрение зависимостей) in FastAPI?

Using `Depends()` to inject (внедрять) shared logic into endpoints — like getting a DB session, verifying auth, or reading config. FastAPI resolves and caches dependencies automatically.

## What is Pydantic used for?

Data validation (проверка данных) and serialization (сериализация). Define a schema with type hints, and Pydantic automatically validates input, converts types, and raises errors for invalid data.

## What is `BaseModel` in Pydantic?

The base class for all Pydantic models. Inherit from it to define a schema with typed fields. FastAPI uses it for request/response bodies.

## How does Pydantic validation work?

When you instantiate (создаёшь экземпляр) a model, Pydantic checks each field against its type. If invalid, it raises a `ValidationError` with a clear message. FastAPI catches it and returns a 422 response.

## What is `str | None = None` in a Pydantic model?

A field that accepts a string or `None`, with a default value of `None` — making it optional (необязательный). The request can omit this field entirely.

## Why can't we use `from` as a field name in Python/Pydantic?

`from` is a reserved keyword (зарезервированное слово) in Python. Workaround: name the field `from_` in the schema and manually rename it when parsing external data.

## What is the difference between `docker build` and `docker compose up`?

`docker build` builds a single image from a Dockerfile. `docker compose up` starts all services defined in `docker-compose.yml`, building images if needed, and manages networking between them.

## What is a volume mount (монтирование тома) and why use it?

Maps a directory from your host machine into the container. Changes on the host appear instantly inside the container. Used for hot reload in development.

```yaml
volumes:
  - ./app:/app/app
```

## What is `--reload` in uvicorn for?

Makes uvicorn watch for file changes and restart automatically. Only use in development — adds overhead (накладные расходы).

## What is `host.docker.internal`?

A special DNS name in Docker on Mac/Windows that resolves (разрешается) to the host machine's IP. Used to reach services running on the host (like LM Studio) from inside a container.

## What is a healthcheck in docker-compose?

A command that Docker runs periodically (периодически) inside a container to check if the service is ready. Other services can wait for it with `depends_on: condition: service_healthy`.

## What is the difference between a named volume and a bind mount?

Bind mount: maps a specific host path into the container. Named volume: Docker manages the storage location — data persists (сохраняется) between container restarts but you don't control where it lives on disk.

## What does `EXPOSE` do in a Dockerfile?

Documents which port the container listens on — it's informational (информационный) only. It does NOT actually publish the port. You still need `-p 8000:8000` in `docker run` or `ports:` in docker-compose.

## What does `uv sync --frozen --no-dev` do?

Installs dependencies exactly as specified in `uv.lock` (`--frozen`) without dev dependencies (`--no-dev`). Ensures reproducible (воспроизводимые), minimal production builds.

## What is a graph database?

A database that stores data as nodes (entities) and relationships (edges) between them. Optimized (оптимизирован) for traversing (обходить) connected data — much faster than SQL JOINs for deep relationships.

## What is the difference between a node and a relationship in Neo4j?

Node — an entity (person, company, location). Relationship — a directed (направленная) connection between two nodes with a type (FOUNDED, WORKS_AT). Both can have properties.

## What is `MERGE` vs `CREATE` in Cypher?

`CREATE` always creates a new node/relationship. `MERGE` creates it only if it doesn't already exist — acts as an upsert (вставить или обновить). Prevents (предотвращает) duplicates.

## What is `ON CREATE SET` vs `ON MATCH SET` in Neo4j?

`ON CREATE SET` runs only when MERGE creates a new node. `ON MATCH SET` runs only when MERGE finds an existing one. Useful for setting `created` timestamp only once, but always updating `embedding`.

## What is `DETACH DELETE` in Cypher?

Deletes a node AND all its relationships. Plain `DELETE` fails if the node has relationships. `DETACH DELETE` removes everything safely.

## What is a vector index in Neo4j?

An index that stores high-dimensional (многомерные) vectors on nodes and supports similarity search — finding nodes whose vectors are closest to a query vector. Used for semantic (смысловой) search.

## What is cosine similarity (косинусное сходство)?

A metric (метрика) that measures the angle between two vectors. Value from 0 to 1 — 1 means identical direction (same meaning), 0 means no similarity. Used to find semantically similar embeddings.

## What is a label in Neo4j?

A tag on a node that categorizes it — e.g. `:Entity`, `:Person`. Labels are required for vector indexes and allow filtering nodes by type in queries.

## What is an embedding (векторное представление)?

A list of numbers (vector) that represents the meaning of text. Similar texts produce similar vectors. Generated by an embedding model like `nomic-embed-text`.

## Why are semantically similar texts close in vector space?

Embedding models are trained to map texts with similar meaning to nearby points in high-dimensional (многомерном) space. "Tesla" and "electric car company" end up close because they co-occur (встречаются вместе) in similar contexts.

## What does `dimensions=768` mean in a vector index?

The length of the embedding vector. `nomic-embed-text-v1.5` outputs 768 numbers per text. The index must match this size exactly.

## What is the difference between keyword search and vector search?

Keyword search matches exact words. Vector search finds semantically similar (семантически похожие) results even if the words are different. "Who started that EV company?" finds Tesla via vector search.

## How does `db.index.vector.queryNodes` work in Neo4j?

Takes an index name, top-k count, and a query vector. Returns the k nodes whose stored embeddings are most similar (cosine) to the query vector, with a similarity score.

## What is RAG (Retrieval-Augmented Generation)?

A pattern where you retrieve (извлекаешь) relevant context from a knowledge base and include it in the prompt before generating an LLM answer. Prevents hallucination (галлюцинация) by grounding responses in facts.

## What is the difference between RAG and GraphRAG?

Regular RAG retrieves text chunks from a vector DB. GraphRAG retrieves structured (структурированные) facts and relationships from a knowledge graph — better for multi-hop (многошаговые) questions that require connecting multiple facts.

## What is a Knowledge Graph (граф знаний)?

A graph where nodes are entities (people, companies, places) and edges are typed relationships between them. Stores structured facts that can be traversed (обходить) and queried.

## What is entity extraction (извлечение сущностей)?

The process of identifying named entities (people, organizations, locations) and relationships from unstructured (неструктурированного) text. In our project, done by the LLM with a strict JSON system prompt.

## What is a system prompt and what is it used for?

A message with `role: "system"` sent before the conversation. Sets the behavior, persona (роль), and output format for the entire conversation. The model treats it as instructions.

## Why is the `/chat` endpoint stateless (без состояния)?

The server stores no session data. The client sends the full conversation history on every request. This makes the server easy to scale — any instance can handle any request.

## Why do we return `context` alongside `answer` in `/query`?

For debugging (отладки) and transparency (прозрачности). You can see exactly what facts were retrieved from Neo4j and passed to the LLM. If the answer is wrong, you can diagnose whether the problem is in retrieval (поиск) or generation.

## What is LM Studio?

A desktop app that runs LLMs locally and exposes an OpenAI-compatible REST API. No internet required, no API costs.

## What is an OpenAI-compatible API?

An API that implements the same endpoints and request/response format as the OpenAI API (`/v1/chat/completions`, `/v1/embeddings`, etc.). You can use the official OpenAI SDK by just changing `base_url`.

## What is `AsyncOpenAI` vs `OpenAI`?

`AsyncOpenAI` makes non-blocking (неблокирующие) HTTP calls using `await` — compatible with async FastAPI endpoints. `OpenAI` is synchronous and blocks the event loop while waiting for a response.

## What does `base_url` do in the OpenAI client?

Overrides the default OpenAI server URL. Set to `http://host.docker.internal:1234/v1` to point to LM Studio instead of OpenAI's servers.

## What is `choices[0].message.content`?

The text of the first generated response. `choices` is a list because the API can return multiple completions (варианты ответа). `[0]` takes the first one, `.message.content` gets the text.

## What is the role `"system"` vs `"user"` vs `"assistant"`?

`system` — instructions for the model (behavior, format, constraints). `user` — human input. `assistant` — previous model responses. Together they form the conversation history.

## What is separation of concerns (разделение ответственности)?

Each module does one thing. Schemas define data shapes, endpoints handle HTTP logic, core modules manage connections and config. Changes in one area don't cascade (распространяться) into others.

## Why put the DB driver in `app/core/db.py`?

The driver maintains a connection pool (пул соединений) — it should be created once and reused across all requests. Centralizing it prevents multiple pools and makes it easy to mock in tests.

## What is `os.getenv("KEY", "default")`?

Reads an environment variable named `KEY`. If it's not set, returns `"default"`. Allows configuration (настройку) without changing code — just set env vars for different environments (dev, prod).

## What is a singleton pattern?

Creating one instance of a resource (DB driver, HTTP client) at module level and reusing it everywhere. Avoids (избегает) the overhead (накладные расходы) of creating a new connection on every request.

## Why generate embeddings as `"{name} {type}"` instead of just `name`?

Adding the type gives the embedding model more context — "Elon Musk Person" is more informative than "Elon Musk". Results in more accurate (точные) similarity search.

## What is the difference between a process and a thread?

A process is an independent (независимый) program with its own memory. A thread runs inside a process and shares memory with other threads. Threads are lighter but need synchronization (синхронизацию) to avoid race conditions.

## What is a deadlock (взаимная блокировка)?

Two or more threads/processes each hold a resource (ресурс) that the other needs, so neither can proceed. They wait for each other forever.

## What is a race condition (состояние гонки)?

When two concurrent (одновременных) operations access shared data and the outcome (результат) depends on their execution order. Can cause unpredictable (непредсказуемые) bugs.

## What is idempotency (идемпотентность)?

An operation is idempotent if calling it multiple times has the same effect as calling it once. GET, PUT, DELETE are idempotent. POST is not. `MERGE` in Neo4j is idempotent.

## What is REST?

An architectural (архитектурный) style for APIs using HTTP. Key constraints: stateless, client-server, uniform interface (единый интерфейс), resources identified by URLs, standard HTTP methods.

## What is the difference between PUT and PATCH?

PUT replaces (заменяет) the entire resource. PATCH partially updates (частично обновляет) only the specified fields.

## What are common HTTP status codes?

- **200** OK
- **201** Created
- **400** Bad Request
- **401** Unauthorized (не авторизован)
- **403** Forbidden (запрещено)
- **404** Not Found
- **422** Unprocessable Entity (невалидные данные)
- **500** Internal Server Error

## What is CORS (Cross-Origin Resource Sharing)?

A browser security mechanism (механизм) that blocks requests from a different domain unless the server explicitly (явно) allows it via response headers. Configure in FastAPI with `CORSMiddleware`.

## What is middleware (промежуточное ПО)?

Code that runs before and after every request. Used for logging (логирование), auth checks, CORS headers, error handling. In FastAPI: `app.add_middleware(...)`.

## What is dependency injection?

A pattern where dependencies (DB sessions, config, auth) are declared as parameters and provided (предоставляются) automatically by the framework. Makes code testable and modular.

## What is horizontal vs vertical scaling?

Vertical (вертикальное) — add more resources (RAM, CPU) to one server. Horizontal (горизонтальное) — add more servers and distribute (распределять) load between them. Horizontal is preferred for high availability (высокой доступности).

## What is a load balancer (балансировщик нагрузки)?

A server that distributes incoming requests across multiple backend instances. Makes horizontal scaling transparent to clients and improves reliability (надёжность).

## What is caching (кэширование) and when to use it?

Storing computed or fetched results temporarily so future requests are faster. Use when: data changes infrequently (редко), computation is expensive (дорогостоящей), same data is requested often.

## What is a message queue (очередь сообщений)?

A buffer (буфер) where producers put tasks and consumers process them asynchronously. Decouples (разделяет) services and handles load spikes (пиковые нагрузки). Examples: Redis, RabbitMQ, Kafka.

## What is eventual consistency (итоговая согласованность)?

A distributed systems model where replicas (реплики) may temporarily be out of sync but will eventually converge (сойдутся) to the same state. Trade-off (компромисс) between availability and consistency.

## What is a microservice (микросервис)?

An independently deployable (развёртываемый) service that does one thing. Communicates with other services via APIs or message queues. Opposite of a monolith (монолит).

## What is the difference between SQL and NoSQL?

SQL — relational (реляционная) DB with fixed schemas, tables, ACID transactions. NoSQL — flexible schemas, various data models (document, graph, key-value). Choose based on data structure and query patterns.

## What is an index in a database?

A data structure that speeds up (ускоряет) queries on a column by avoiding full table scans. Trade-off: faster reads, slower writes, more storage.

## What is a transaction (транзакция)?

A sequence (последовательность) of operations that executes as a single unit — either all succeed or all fail (rollback). Ensures data consistency.

## What is ACID?

Properties of reliable (надёжных) database transactions:

- **A**tomicity (атомарность) — all or nothing
- **C**onsistency (согласованность) — valid state before and after
- **I**solation (изоляция) — transactions don't interfere (не мешают) with each other
- **D**urability (долговечность) — committed data survives crashes

## What is the N+1 query problem?

When fetching a list of N items, then making N separate queries to fetch related data — totaling N+1 queries. Fix: use JOIN or eager loading (жадная загрузка) to fetch everything in one query.

## What is pagination (пагинация)?

Splitting large result sets into pages. Prevents returning (возвращать) millions of rows at once. Implemented with `limit` + `offset` or cursor-based pagination.

## What is JWT (JSON Web Token)?

A self-contained (самодостаточный) token that encodes (кодирует) user identity and claims. Signed with a secret — server can verify it without a DB lookup. Stateless authentication (аутентификация).

## What is OAuth2?

An authorization (авторизация) framework that lets users grant third-party apps access to their resources without sharing passwords. Uses access tokens with limited scope (область действия).

## What is a decorator (декоратор) in Python?

A function that wraps (оборачивает) another function to extend its behavior without modifying it. Used with `@` syntax. FastAPI uses decorators for routing: `@router.post("/chat")`.

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("before")
        result = func(*args, **kwargs)
        print("after")
        return result
    return wrapper
```

## What is a generator (генератор) in Python?

A function that uses `yield` instead of `return`. It produces (производит) values lazily (лениво) — one at a time, without storing all in memory. Useful for large datasets.

```python
def count_up(n):
    for i in range(n):
        yield i
```

## What is a list comprehension (списковое включение)?

A concise (краткий) way to create lists using a single expression.

```python
squares = [x**2 for x in range(10)]
filtered = [x for x in data if x > 0]
```

## What is the difference between `is` and `==` in Python?

`==` checks value equality (равенство значений). `is` checks identity (идентичность) — whether two variables point to the same object in memory.

```python
a = [1, 2]
b = [1, 2]
a == b  # True (same value)
a is b  # False (different objects)
```

## What are `*args` and `**kwargs`?

`*args` collects (собирает) extra positional (позиционных) arguments as a tuple. `**kwargs` collects extra keyword arguments as a dict. Used to write flexible functions that accept any number of arguments.

## What is the difference between a shallow copy and a deep copy?

Shallow copy (поверхностная копия) — copies the object but nested objects are still shared. Deep copy (глубокая копия) — copies everything recursively (рекурсивно), no shared references.

```python
import copy
shallow = copy.copy(obj)
deep = copy.deepcopy(obj)
```

## What is `__init__` in Python?

The constructor (конструктор) method of a class — called automatically when a new instance (экземпляр) is created. Used to initialize (инициализировать) attributes.

## What is the difference between `@classmethod` and `@staticmethod`?

`@classmethod` receives the class (`cls`) as the first argument — can access and modify class state. `@staticmethod` receives no implicit (неявного) first argument — it's just a regular function namespaced inside the class.

## What is `__str__` vs `__repr__`?

`__str__` — human-readable (читаемый) string representation, used by `print()`. `__repr__` — unambiguous (однозначное) developer representation, used in the REPL and debugger. If only one is defined, `__repr__` is used as fallback (запасной вариант).

## What is inheritance (наследование) in Python?

A class can inherit (наследовать) attributes and methods from a parent class. Python supports multiple inheritance.

```python
class Animal:
    def speak(self): ...

class Dog(Animal):
    def speak(self):
        return "Woof"
```

## What is encapsulation (инкапсуляция)?

Hiding internal (внутреннего) implementation details and exposing only a public interface. In Python: single underscore `_attr` = convention for internal use, double underscore `__attr` = name mangling.

## What is polymorphism (полиморфизм)?

Different classes implementing the same interface or method name, each with their own behavior. Python achieves (достигает) this via duck typing — if it has the right methods, it works.

## What is abstraction (абстракция)?

Hiding complexity (сложность) behind a simple interface. You use a database driver without knowing how it manages connections internally.

## What are SOLID principles?

- **S** — Single Responsibility (единственная ответственность): one class, one job
- **O** — Open/Closed (открыт/закрыт): open for extension (расширение), closed for modification
- **I** — Interface Segregation (разделение интерфейсов): don't force classes to implement methods they don't need
- **L** — Liskov Substitution (подстановка): subclasses should be substitutable for parent classes
- **D** — Dependency Inversion (инверсия зависимостей): depend on abstractions, not implementations

## What is a context manager (менеджер контекста)?

An object that defines `__enter__` and `__exit__` methods, used with `with` statement. Guarantees (гарантирует) cleanup (очистка) even if an error occurs.

```python
with open("file.txt") as f:
    data = f.read()
# file is closed automatically
```

## What is `asynccontextmanager` in Python?

A decorator from `contextlib` that turns an async generator function into a context manager. Used in FastAPI's `lifespan`. `yield` separates startup from shutdown.

## What is the difference between `append` and `extend` on a list?

`append` adds a single element. `extend` adds all elements from an iterable (итерируемого объекта).

```python
lst = [1, 2]
lst.append([3, 4])   # [1, 2, [3, 4]]
lst.extend([3, 4])   # [1, 2, 3, 4]
```

## What is a dict comprehension (словарное включение)?

```python
squares = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
```

## What is `enumerate()` in Python?

Returns (возвращает) pairs of (index, value) when iterating. Avoids manually tracking (отслеживать) the index.

```python
for i, item in enumerate(["a", "b", "c"]):
    print(i, item)
```

## What is `zip()` in Python?

Combines (объединяет) multiple iterables element by element into tuples.

```python
names = ["Alice", "Bob"]
scores = [90, 85]
for name, score in zip(names, scores):
    print(name, score)
```

## What is a lambda function?

An anonymous (анонимная) inline function with a single expression. Used for short callbacks.

```python
double = lambda x: x * 2
sorted_list = sorted(items, key=lambda x: x.name)
```

## What is `map()` and `filter()`?

`map(func, iterable)` — applies (применяет) a function to every element. `filter(func, iterable)` — keeps only elements where the function returns `True`. Both return iterators (итераторы).

## What is the difference between `tuple` and `list`?

List is mutable (изменяемый) — you can add/remove elements. Tuple is immutable (неизменяемый) — fixed after creation. Tuples are faster and can be used as dict keys.

## What is a `set` in Python?

An unordered (неупорядоченная) collection of unique (уникальных) elements. Fast membership checks (O(1)). Supports union (объединение), intersection (пересечение), difference.

## What is type hinting (аннотация типов) in Python?

Adding type annotations to variables and function signatures for documentation and static analysis (статического анализа). Not enforced at runtime — tools like mypy check them.

```python
def greet(name: str) -> str:
    return f"Hello, {name}"
```

## What is `Optional[str]` in Python type hints?

Equivalent (эквивалент) to `str | None` — the value can be a string or `None`. From the `typing` module (deprecated in favor of `str | None` in Python 3.10+).

## What is `dataclass` in Python?

A decorator that auto-generates (автоматически генерирует) `__init__`, `__repr__`, `__eq__` for a class based on its annotated fields. Cleaner alternative to writing boilerplate (шаблонный код).

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
```

## What is `pytest`?

The standard Python testing framework. Tests are plain functions starting with `test_`. Auto-discovers (автоматически находит) test files matching `test_*.py`.

```python
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
```

## What is a fixture (фикстура) in pytest?

A reusable (переиспользуемый) setup function decorated with `@pytest.fixture`. Injected into tests automatically by name. Used for DB connections, test clients, mock objects.

## What is mocking (имитация) in tests?

Replacing a real dependency with a fake object that simulates (симулирует) its behavior. Allows testing code in isolation without real DB/network calls.

```python
from unittest.mock import patch

@patch("app.core.db.driver")
def test_ingest(mock_driver):
    ...
```

## What is `TestClient` in FastAPI?

A synchronous (синхронный) HTTP client from `httpx` used to test FastAPI endpoints without running a real server. Provided by `from fastapi.testclient import TestClient`.

## What is the difference between unit tests and integration tests?

Unit tests — test a single function in isolation (изоляции), with mocks. Integration tests — test multiple components together (real DB, real HTTP). Both are necessary (необходимы).

## What is `assert` in Python?

A statement that raises `AssertionError` if the condition is `False`. Used in tests and for debugging invariants (инварианты).

```python
assert result == 200, f"Expected 200, got {result}"
```

## What is `git rebase` vs `git merge`?

`merge` — combines (объединяет) branches, creates a merge commit, preserves (сохраняет) history. `rebase` — moves commits on top of another branch, creates linear (линейную) history. Use rebase for clean history, merge for collaboration (совместная работа).

## What is a git conflict (конфликт)?

When two branches modify the same lines — Git can't automatically choose which version to keep. You must manually resolve (разрешить) the conflict and commit.

## What is `git stash`?

Temporarily (временно) saves uncommitted (незафиксированные) changes so you can switch branches without committing. `git stash pop` restores (восстанавливает) them.

## What is a `.gitignore` file?

A file listing paths and patterns that Git should not track. Common entries: `.env`, `__pycache__/`, `.venv/`, `*.pyc`, `node_modules/`.

## What is a pull request (PR)?

A request to merge (слить) a branch into the main branch. Includes code review (ревью кода), discussion, and CI checks before merging.

## What is CI/CD?

- **CI** (Continuous Integration — непрерывная интеграция): automatically run tests on every push
- **CD** (Continuous Deployment/Delivery — непрерывное развёртывание): automatically deploy (развёртывать) passing builds to production

## What is an environment variable (переменная окружения)?

A key-value pair set in the OS environment. Used to configure (настраивать) apps without hardcoding secrets. Read in Python with `os.getenv("KEY")`.

## What is a `.env` file?

A file containing environment variables in `KEY=VALUE` format. Loaded by tools like `python-dotenv`. Never commit (коммитить) `.env` to git — it contains secrets.

## What is the difference between authentication and authorization?

Authentication (аутентификация) — verifying who you are (username + password, JWT). Authorization (авторизация) — verifying what you're allowed to do (permissions, roles).

## What is hashing (хэширование)?

Converting data into a fixed-size string (hash). One-way — you can't reverse (обратить) it. Used for storing passwords. Common algorithms: SHA-256, bcrypt.

## What is SQL injection?

An attack where malicious (вредоносный) SQL is inserted into a query. Prevented (предотвращается) by using parameterized queries (параметризованные запросы) — never concatenate (конкатенировать) user input into SQL strings.

## What is XSS (Cross-Site Scripting)?

An attack where malicious JavaScript is injected into a webpage and executed in other users' browsers. Prevented by escaping (экранирование) user input in HTML output.

## What is a foreign key (внешний ключ)?

A column in one table that references (ссылается на) the primary key of another table. Enforces (обеспечивает) referential integrity (ссылочная целостность) — prevents orphaned records.

## What is normalization (нормализация) in databases?

Organizing data to reduce redundancy (избыточность) and improve consistency. Split data into related tables instead of repeating the same values in one big table.

## What is denormalization (денормализация)?

Intentionally (намеренно) duplicating data across tables to speed up read queries. Trade-off: faster reads, harder to keep data consistent (согласованным).

## What is a primary key (первичный ключ)?

A column (or set of columns) that uniquely identifies (однозначно идентифицирует) each row in a table. Must be unique and not null.

## What is an ORM (Object-Relational Mapper)?

A library that maps (отображает) database tables to Python classes. You write Python instead of SQL. Examples: SQLAlchemy, Django ORM. Trade-off: convenient (удобно) but can hide performance issues.

## What is connection pooling (пул соединений)?

Maintaining a set of reusable database connections instead of creating a new one per request. Reduces (уменьшает) latency (задержку) and DB server load.

## What is lazy loading vs eager loading?

Lazy loading (ленивая загрузка) — related data is fetched only when accessed. Eager loading (жадная загрузка) — related data is fetched upfront in the same query. Eager loading prevents N+1 problem.

## What is Redis?

An in-memory (в памяти) key-value store used for caching, session storage, message queues, rate limiting. Extremely fast — microsecond latency (задержка в микросекундах).

## What is rate limiting (ограничение частоты запросов)?

Restricting (ограничивая) how many requests a client can make in a time window. Protects (защищает) the API from abuse (злоупотребления) and DDoS attacks.

## What is WebSocket?

A protocol (протокол) providing full-duplex (двунаправленный) persistent (постоянный) connection between client and server. Unlike HTTP, the server can push (отправлять) data without a client request. Used for chat, live updates.

## What is gRPC?

A high-performance (высокопроизводительный) RPC framework using Protocol Buffers for serialization. Faster than REST/JSON for inter-service (межсервисное) communication. Used between microservices.

## What is a reverse proxy (обратный прокси)?

A server that sits (находится) in front of backend servers and forwards (перенаправляет) client requests to them. Examples: Nginx, Caddy. Handles SSL termination (завершение), load balancing, caching.

## What is SSL/TLS?

Protocols (протоколы) that encrypt (шифруют) data in transit (передаваемые). HTTPS = HTTP over TLS. Prevents eavesdropping (перехват) and man-in-the-middle attacks.

## What is a CDN (Content Delivery Network)?

A geographically (географически) distributed network of servers that cache (кэшируют) static assets (статические файлы) close to users. Reduces latency (задержку) and server load.

## What is observability (наблюдаемость)?

The ability to understand what's happening inside a system from its outputs. Three pillars (столпа): logs (логи), metrics (метрики), traces (трассировки).

## What is structured logging (структурированное логирование)?

Writing logs as JSON instead of plain text. Makes it easy to search (искать), filter, and aggregate (агрегировать) logs in tools like Datadog or ELK stack.

## What is a health check endpoint?

An endpoint (usually `GET /health`) that returns 200 if the service is running correctly. Used by load balancers and orchestrators (оркестраторы) like Kubernetes to route traffic only to healthy instances.

## What is Kubernetes (K8s)?

A container orchestration (оркестрация) platform that automates (автоматизирует) deployment, scaling, and management of containerized applications. Manages multiple Docker containers across multiple machines.

## What is a Docker image vs a container?

Image — a read-only (только для чтения) blueprint (шаблон) built from a Dockerfile. Container — a running instance (запущенный экземпляр) of an image. Multiple containers can run from one image.

## What is `docker compose exec` vs `docker compose run`?

`exec` — runs a command inside an already running (запущенном) container. `run` — starts a new temporary (временный) container from the service image.

## What is multistage build (многоэтапная сборка) in Docker?

Using multiple `FROM` statements in a Dockerfile to build in one stage and copy only the result to a smaller final image. Reduces (уменьшает) image size by excluding build tools.

## What is `.dockerignore`?

Like `.gitignore` but for Docker builds — lists files to exclude (исключить) from the build context. Speeds up builds and prevents accidentally copying secrets into the image.

## What is the difference between `CMD` and `ENTRYPOINT` in Dockerfile?

`ENTRYPOINT` — the main command that always runs. `CMD` — default arguments that can be overridden (переопределены) at runtime. Together: `ENTRYPOINT` is the executable, `CMD` is its default args.

## What is `uvicorn` and why use it with FastAPI?

An ASGI (Asynchronous Server Gateway Interface) server that runs async Python web apps. FastAPI is an ASGI app — it needs uvicorn (or hypercorn) to handle HTTP connections.

## What is ASGI vs WSGI?

WSGI — synchronous (синхронный) Python server standard (Django, Flask). ASGI — asynchronous standard that supports async handlers and WebSockets. FastAPI requires ASGI.

## What is Pydantic `Field()`?

Allows extra validation and metadata (метаданные) on a schema field: min/max values, regex, description, example.

```python
class User(BaseModel):
    age: int = Field(gt=0, lt=150, description="User age")
    email: str = Field(pattern=r".+@.+")
```

## What is `HTTPException` in FastAPI?

A special exception that FastAPI converts into an HTTP error response with a status code and detail message.

```python
raise HTTPException(status_code=404, detail="User not found")
```

## What is background task (фоновая задача) in FastAPI?

A function that runs after the response is sent to the client. Used for non-critical (некритичных) work like sending emails or logging.

```python
@router.post("/notify")
async def notify(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, "hello")
    return {"status": "queued"}
```

## What is `Annotated` in Python type hints?

Allows attaching (прикреплять) metadata to a type hint. FastAPI uses it to combine type + `Depends()` or `Field()` in one annotation.

```python
from typing import Annotated
UserId = Annotated[int, Path(gt=0)]
```

## What is an abstract class (абстрактный класс)?

A class that cannot be instantiated (создать экземпляр) directly — it defines an interface that subclasses must implement. Uses `ABC` and `@abstractmethod` from `abc` module.

## What is duck typing (утиная типизация)?

"If it walks like a duck and quacks like a duck, it's a duck." Python doesn't check types at runtime — if an object has the right methods, it works. No need for explicit interfaces.

## What is the difference between `__new__` and `__init__`?

`__new__` creates (создаёт) the object — called first, returns the new instance. `__init__` initializes (инициализирует) it — called after, sets attributes. Usually you only need `__init__`.

## What is `property` decorator in Python?

Turns a method into a read-only (только для чтения) attribute. Lets you add validation or computation (вычисление) while keeping clean attribute access syntax.

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def area(self):
        return 3.14 * self._radius ** 2
```

## What is method resolution order (MRO — порядок разрешения методов)?

The order Python searches (ищет) for methods in a class hierarchy with multiple inheritance. Use `ClassName.mro()` to inspect it. Follows C3 linearization algorithm.

## What is `super()` in Python?

Calls the method from the parent class. Essential (необходим) in multiple inheritance to ensure all parents are properly initialized.

```python
class Child(Parent):
    def __init__(self):
        super().__init__()
```

## What is pickling (сериализация через pickle)?

Converting a Python object to a byte stream (поток байтов) for storage or transfer. `pickle.dumps()` serializes, `pickle.loads()` deserializes. ProcessPoolExecutor uses pickle to pass data between processes.

## What is recursion (рекурсия)?

A function that calls itself. Must have a base case (базовый случай) to stop. Python has a default recursion limit of 1000 (`sys.setrecursionlimit()`).

## What is Big O notation?

A way to describe algorithm efficiency (эффективность) as input size grows. Common complexities:
- O(1) — constant (константное)
- O(log n) — logarithmic (логарифмическое)
- O(n) — linear (линейное)
- O(n²) — quadratic (квадратичное)

## What is the difference between a stack and a queue?

Stack (стек) — LIFO (Last In, First Out — последним пришёл, первым ушёл). Queue (очередь) — FIFO (First In, First Out — первым пришёл, первым ушёл).

## What is a hash table (хэш-таблица)?

A data structure that maps keys to values using a hash function. Average O(1) lookup. Python `dict` and `set` are implemented as hash tables.

## What is binary search (бинарный поиск)?

A search algorithm (алгоритм) that works on sorted (отсортированных) arrays. Repeatedly (многократно) halves (делит пополам) the search space — O(log n) vs O(n) for linear search.

## What is a linked list (связный список)?

A data structure where each node contains a value and a pointer (указатель) to the next node. O(1) insertion at head, O(n) lookup. Python `list` is not a linked list — it's a dynamic array.

## What is memoization (мемоизация)?

Caching (кэширование) the results of expensive function calls so the same inputs return the cached result instead of recomputing. Implemented with `functools.lru_cache`.

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

## What is `functools.partial`?

Creates a new function with some arguments pre-filled (предзаполненными).

```python
from functools import partial
double = partial(lambda x, y: x * y, y=2)
double(5)  # 10
```

## What is the walrus operator `:=`?

Assigns (присваивает) and returns a value in a single expression. Added in Python 3.8.

```python
if (n := len(data)) > 10:
    print(f"Too long: {n}")
```

## What is `pathlib` in Python?

A modern (современный) module for file system paths. Object-oriented (объектно-ориентированный) alternative to `os.path`.

```python
from pathlib import Path
p = Path("app") / "core" / "llm.py"
content = p.read_text()
```

## What is `asyncio.gather()`?

Runs multiple coroutines concurrently (одновременно) and waits for all to complete. Returns a list of results.

```python
results = await asyncio.gather(
    fetch_user(1),
    fetch_user(2),
    fetch_user(3),
)
```

## What is `asyncio.wait_for()`?

Runs a coroutine with a timeout (таймаут). Raises `asyncio.TimeoutError` if it takes too long.

```python
try:
    result = await asyncio.wait_for(long_task(), timeout=5.0)
except asyncio.TimeoutError:
    print("Too slow!")
```

## What is `asyncio.Lock()`?

An async mutex (мьютекс) that ensures (обеспечивает) only one coroutine at a time accesses a shared resource. Prevents race conditions in async code.

## What is `aiohttp`?

An async HTTP client/server library. Alternative to `httpx` for making async HTTP requests. `httpx` is preferred with FastAPI because it's compatible with both sync and async.

## What is `httpx`?

A modern (современный) HTTP client that supports both sync and async usage. Used by FastAPI's `TestClient`. Supports HTTP/2 and connection pooling.

## What is the difference between `requests` and `httpx`?

`requests` is synchronous only — blocks the event loop. `httpx` supports async — use `async with httpx.AsyncClient() as client: await client.get(...)`. Use `httpx` in async codebases.

## What is `Depends()` in FastAPI?

A function that declares a dependency to be injected (внедрённой) into an endpoint. FastAPI calls it, caches the result, and passes it as an argument.

```python
async def get_db():
    async with driver.session() as session:
        yield session

@router.get("/users")
async def get_users(db=Depends(get_db)):
    ...
```

## What is `yield` in a FastAPI dependency?

Allows the dependency to have setup AND teardown (очистка) logic. Everything before `yield` runs before the request, everything after runs after the response is sent.

## What is an API gateway (шлюз API)?

A single entry point (точка входа) for all client requests. Routes (маршрутизирует) to the correct microservice, handles auth, rate limiting, logging. Examples: Kong, AWS API Gateway.

## What is service discovery (обнаружение сервисов)?

A mechanism (механизм) that allows microservices to find each other without hardcoding (захардкоживания) addresses. Services register themselves in a registry (реестр) and query it to find others.

## What is the CAP theorem?

A distributed system can only guarantee (гарантировать) two of three:
- **C**onsistency (согласованность) — all nodes see the same data
- **A**vailability (доступность) — every request gets a response
- **P**artition tolerance (устойчивость к разделению) — works despite network failures

## What is a singleton in Python?

A class that allows only one instance to exist. In practice, Python modules are singletons — importing the same module twice gives the same object.

## What is the factory pattern (фабричный метод)?

A creational (порождающий) pattern where a method creates objects without specifying the exact class. Useful when the type of object to create depends on runtime conditions (условий).

## What is the observer pattern (наблюдатель)?

Objects (observers) subscribe (подписываются) to events from a subject. When the subject changes, all observers are notified (уведомляются). Used in event-driven (событийно-ориентированных) systems.

## What is the repository pattern?

Abstracts (абстрагирует) data access behind an interface. Endpoints talk to a repository, not directly to the DB. Makes it easy to swap (заменить) the DB or mock it in tests.

## What is `__slots__` in Python?

A class variable that restricts (ограничивает) which attributes an instance can have. Reduces memory usage (потребление памяти) by avoiding the per-instance `__dict__`.

## What is a metaclass (метакласс)?

A class of a class — defines how a class behaves when created. Used in frameworks (Django models, SQLAlchemy) to add behavior to classes automatically. Advanced topic.

## What is `typing.Protocol`?

Defines a structural interface (структурный интерфейс) — any class that implements the required methods satisfies the protocol without explicit inheritance. Python's approach to interfaces.

## What is `__call__` in Python?

Makes an instance callable (вызываемым) like a function. Useful for function-like objects that need to maintain state.

```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor
    def __call__(self, x):
        return x * self.factor

double = Multiplier(2)
double(5)  # 10
```

## What is `itertools` module?

A standard library module with efficient (эффективными) iterators for common patterns: `chain`, `product`, `combinations`, `permutations`, `groupby`. Avoids creating large intermediate (промежуточных) lists.

## What is a semaphore (семафор)?

A concurrency (параллелизма) primitive that limits the number of concurrent (одновременных) accesses to a resource. `asyncio.Semaphore(10)` allows max 10 coroutines at once.

## What is `__enter__` and `__exit__`?

Methods that implement the context manager protocol. `__enter__` runs at `with` entry (вход), `__exit__` runs at exit — even if an exception (исключение) occurred.

## What is `typing.TypeVar`?

Creates a generic (универсальный) type variable for generic functions and classes — functions that work with any type but maintain type consistency.

```python
from typing import TypeVar
T = TypeVar("T")

def first(lst: list[T]) -> T:
    return lst[0]
```

## What is `collections.defaultdict`?

A dict that automatically creates a default value for missing keys instead of raising `KeyError`.

```python
from collections import defaultdict
counts = defaultdict(int)
counts["a"] += 1  # no KeyError
```

## What is `collections.Counter`?

A dict subclass (подкласс) for counting hashable objects. Most common use: count word frequencies (частоты).

```python
from collections import Counter
c = Counter(["a", "b", "a", "c", "a"])
c.most_common(2)  # [("a", 3), ("b", 1)]
```

## What is `heapq` in Python?

A module implementing a min-heap (минимальная куча). Efficient (эффективный) for finding smallest/largest elements, priority queues. O(log n) push/pop.

## What is the difference between `os.path` and `pathlib`?

`os.path` is older, function-based (функциональный). `pathlib.Path` is object-oriented (объектно-ориентированный) and more readable. Prefer `pathlib` in modern code.

## What is a linter (линтер)?

A tool that statically analyzes (статически анализирует) code for errors, style issues, and anti-patterns (антипаттерны) without running it. We use `ruff` — combines linting and formatting.

## What is `ruff` and why use it?

An extremely fast Python linter and formatter written in Rust. Replaces (заменяет) flake8, isort, black in one tool. Run: `ruff check .` and `ruff format .`

## What is type narrowing (сужение типа)?

When Python/mypy knows a more specific type inside a branch due to a runtime check.

```python
def process(x: str | None):
    if x is None:
        return  # here x is None
    print(x.upper())  # here x is str
```

## What is `__all__` in a Python module?

A list of names that should be exported when `from module import *` is used. Controls the public API (публичный API) of a module.

## What is `importlib` used for?

Provides (предоставляет) programmatic (программный) access to Python's import system. Used to dynamically import (динамически импортировать) modules at runtime.

## What is monkey patching (monkey patching)?

Dynamically (динамически) modifying a class or module at runtime. Common in tests to replace (заменить) real implementations with mocks. Generally considered a code smell (запах кода) in production.

## What is `__pycache__`?

A directory where Python stores compiled (скомпилированный) bytecode (`.pyc` files) for faster import on subsequent runs. Should be in `.gitignore`.

## What is the Global Interpreter Lock (GIL)?

A mutex (мьютекс) in CPython that allows only one thread to execute Python bytecode at a time. Prevents (предотвращает) true parallelism (параллелизм) for CPU-bound threads. Not present in PyPy or Python 3.13 free-threaded mode.

## What is `sys.path` in Python?

A list of directories that Python searches (ищет) when importing modules. You can append (добавлять) to it to import from custom (пользовательских) locations.

## What is an abstract base class (ABC)?

A class using `abc.ABC` that defines methods subclasses must implement. Raises `TypeError` if you try to instantiate (создать экземпляр) it or a subclass that doesn't implement all abstract methods.

## What is `namedtuple` in Python?

A tuple subclass (подкласс) with named fields. Immutable (неизменяемый) like a tuple but readable like a class. Lighter than a dataclass.

```python
from collections import namedtuple
Point = namedtuple("Point", ["x", "y"])
p = Point(1, 2)
p.x  # 1
```

## What is the difference between `__getattr__` and `__getattribute__`?

`__getattr__` is called only when an attribute is NOT found normally. `__getattribute__` is called on EVERY attribute access (доступ). Override `__getattr__` for dynamic attributes, be careful with `__getattribute__`.

## What is `weakref` in Python?

A reference (ссылка) to an object that doesn't prevent (не препятствует) it from being garbage collected (удалённым сборщиком мусора). Useful for caches that shouldn't keep objects alive unnecessarily (без необходимости).

## What is `functools.lru_cache` and when to use it?

A decorator (декоратор) that caches (кэширует) the results of a function based on its arguments. Use for pure (чистых) functions that are expensive (затратных) to compute and called repeatedly with the same inputs.

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

## What is `functools.partial`?

Creates a new function with some arguments pre-filled (заранее заданными). Useful for reducing (уменьшения) the number of arguments a function requires.

```python
from functools import partial
multiply = lambda x, y: x * y
double = partial(multiply, 2)
double(5)  # 10
```

## What is the difference between `is` and `==` in Python?

`==` compares values (значения). `is` compares identity (идентичность) — whether two variables point to the exact same object in memory. Use `is` only for `None`, `True`, `False`.

## What is `enumerate` and when to use it?

Built-in that returns index-value pairs from an iterable (итерируемого). Cleaner than using a counter variable manually.

```python
for i, val in enumerate(["a", "b", "c"]):
    print(i, val)  # 0 a, 1 b, 2 c
```

## What is `zip` in Python?

Combines (объединяет) multiple iterables element by element into tuples. Stops at the shortest iterable.

```python
names = ["Alice", "Bob"]
scores = [95, 87]
for name, score in zip(names, scores):
    print(name, score)
```

## What is `*args` and `**kwargs`?

`*args` collects (собирает) extra positional (позиционных) arguments into a tuple. `**kwargs` collects extra keyword (именованных) arguments into a dict. Used when a function needs to accept (принимать) arbitrary (произвольное) number of arguments.

## What is a context manager and how to create one?

An object that defines `__enter__` and `__exit__` methods, used with `with`. Guarantees (гарантирует) cleanup (очистку) even if an exception (исключение) occurs.

```python
class Timer:
    def __enter__(self):
        self.start = time.time()
        return self
    def __exit__(self, *args):
        print(time.time() - self.start)
```

## What is `dataclass` in Python?

A decorator that auto-generates `__init__`, `__repr__`, `__eq__` from class annotations (аннотаций). Less verbose (многословный) than writing them manually. Similar to Pydantic but without runtime validation.

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
```

## What is the difference between shallow copy and deep copy?

Shallow copy (поверхностная копия) copies the outer object but nested (вложенные) objects are still shared (разделены). Deep copy (глубокая копия) recursively (рекурсивно) copies everything. Use `copy.deepcopy()` when you need complete independence (независимость).

## What is `typing.TypeVar`?

Used to define generic (обобщённые) functions or classes that work with different types while preserving (сохраняя) type information. Enables (позволяет) the type checker to track what type is passed.

```python
from typing import TypeVar
T = TypeVar("T")
def first(items: list[T]) -> T:
    return items[0]
```

## What is the difference between `raise` and `raise e` and `raise e from e2`?

`raise` re-raises (повторно выбрасывает) the current exception preserving (сохраняя) the traceback. `raise e` raises `e` but replaces the traceback. `raise e from e2` chains (связывает) exceptions explicitly (явно), making the cause clear.

## What is exception chaining in Python?

When one exception is raised (выбрасывается) while handling another, Python links (связывает) them. `raise X from Y` makes Y the explicit (явная) cause. `raise X` inside `except` makes the original exception the implicit (неявная) context.

## What is `asyncio.gather` vs `asyncio.wait`?

`gather` runs coroutines concurrently (параллельно) and returns results in order — cancels all if one raises by default. `wait` gives more control: returns done/pending sets, allows choosing when to stop (FIRST_COMPLETED, FIRST_EXCEPTION, ALL_COMPLETED).

## What is backpressure (обратное давление) in async systems?

When a consumer (потребитель) can't process (обрабатывать) data as fast as a producer (производитель) sends it. Solutions: queues with max size, rate limiting (ограничение скорости), circuit breakers (предохранители).

## What is rate limiting (ограничение частоты запросов)?

Restricting (ограничение) how many requests a client can make in a time window. Protects (защищает) services from overload (перегрузки). Common algorithms: token bucket (токен-корзина), sliding window (скользящее окно), fixed window.

## What is a circuit breaker (автоматический выключатель) pattern?

Prevents (предотвращает) cascading (каскадных) failures by stopping requests to a failing service. States: Closed (normal), Open (failing — block requests), Half-Open (testing recovery). Common in microservices.

## What is idempotency (идемпотентность) and why does it matter for APIs?

An operation is idempotent if calling it multiple times produces the same result as calling it once. GET, PUT, DELETE should be idempotent. POST generally isn't. Critical for retries (повторных попыток) and distributed systems.

## What is the difference between authentication (аутентификация) and authorization (авторизация)?

Authentication = verifying (проверка) who you are (identity). Authorization = verifying what you are allowed (разрешено) to do (permissions). "Login" is authentication; "can this user delete this post" is authorization.

## What is HTTPS and how does TLS work?

HTTPS = HTTP over TLS (Transport Layer Security). TLS establishes (устанавливает) an encrypted (зашифрованный) connection via handshake (рукопожатие): server sends certificate (сертификат), client verifies it, they negotiate (согласуют) a session key, all traffic is encrypted.

## What is the difference between symmetric and asymmetric encryption (шифрование)?

Symmetric: same key (ключ) to encrypt (зашифровать) and decrypt (расшифровать) — fast, used for bulk (массовых) data (e.g. AES). Asymmetric: public key encrypts, private key decrypts — slower, used for key exchange (обмена ключами) and signatures (e.g. RSA, ECDSA).

## What is SQL injection and how to prevent it?

Attacker (злоумышленник) injects (вводит) SQL code through user input to manipulate (манипулировать) the database. Prevention: always use parameterized queries (параметризованные запросы) / prepared statements (подготовленные запросы), never string-concatenate (конкатенировать) user input into SQL.

## What is XSS (Cross-Site Scripting)?

Attacker injects (вводит) malicious (вредоносный) JavaScript into web pages viewed by other users. Prevention: escape (экранировать) output, use Content-Security-Policy header, avoid `innerHTML` with untrusted (ненадёжным) content.

## What is CSRF (Cross-Site Request Forgery)?

Tricks (заставляет обманом) a logged-in user's browser into sending an unwanted (нежелательный) request to a site. Prevention: CSRF tokens (уникальный токен per session), SameSite cookie attribute, checking Origin header.

## What is the difference between `GET` and `POST` in HTTP?

`GET` retrieves (получает) data — parameters in URL, cacheable (кэшируемый), idempotent. `POST` sends data to create/process — body payload (тело запроса), not cached, not idempotent. Don't use GET for sensitive (конфиденциальных) data as it appears in logs and history.

## What is HTTP/2 and how does it differ from HTTP/1.1?

HTTP/2: multiplexing (мультиплексирование) — multiple requests over one connection simultaneously (одновременно). HTTP/1.1: one request at a time per connection (or pipelining with issues). HTTP/2 also has header compression (сжатие) and server push.

## What is a webhook?

A callback (обратный вызов) over HTTP — a service sends a POST request to your URL when an event (событие) occurs. The reverse (обратное) of polling: instead of you asking "anything new?", the service tells you. Common in payment systems, GitHub, Stripe.

## What is GraphQL and how does it differ from REST?

GraphQL: client specifies (указывает) exactly what fields (поля) it needs in one request. REST: fixed endpoints return fixed shapes (формы). GraphQL solves over-fetching (избыточная загрузка) and under-fetching (недостаточная загрузка) but adds complexity on the server.

## What is the N+1 query problem?

When fetching a list of N items triggers N additional queries for related data (смежных данных). Example: fetch 100 users, then 100 separate queries for each user's posts. Solution: eager loading (жадная загрузка) / `JOIN`, or DataLoader batching (пакетная обработка).

## What is database sharding (шардирование)?

Splitting (разделение) a database horizontally (горизонтально) across multiple machines — each shard (шард) holds a subset (подмножество) of the data. Enables (позволяет) horizontal scaling. Complexity: cross-shard queries, rebalancing (перебалансировка).

## What is eventual consistency (согласованность в конечном счёте)?

In distributed systems (распределённых системах), all nodes will eventually (в конечном итоге) have the same data — but not necessarily immediately (немедленно). Trade-off: higher availability (доступность) vs strong consistency (строгая согласованность). Used in DNS, S3, Cassandra.

## What is CAP theorem?

In a distributed system you can only guarantee two of three: Consistency (согласованность — every read gets the latest write), Availability (доступность — every request gets a response), Partition tolerance (устойчивость к разделению — system works despite network failures). Must choose CA, CP, or AP.

## What is a CDN (Content Delivery Network)?

A network of geographically (географически) distributed servers that cache (кэшируют) static content (статический контент) close to users. Reduces (уменьшает) latency (задержку) and load on origin servers. Common: Cloudflare, AWS CloudFront.

## What is observability (наблюдаемость) in distributed systems?

The ability to understand the internal state of a system from its external outputs. The three pillars (столпа): Logs (логи — events), Metrics (метрики — measurements over time), Traces (трассировки — request flow across services).

## What is `asyncio.timeout` (introduced in Python 3.11)?

A context manager for cancelling (отменяющий) async operations that take too long. Cleaner (чище) than `asyncio.wait_for`.

```python
async with asyncio.timeout(5.0):
    result = await slow_operation()  # raises TimeoutError if > 5s
```
