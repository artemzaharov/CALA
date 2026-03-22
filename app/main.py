from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.db import driver


# lifespan handles startup and shutdown events.
# Everything before yield runs on startup, everything after on shutdown.
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Close the Neo4j driver connection pool gracefully on shutdown.
    await driver.close()


app = FastAPI(title="CALA AI API", version="0.1.0", lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")
