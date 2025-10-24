from __future__ import annotations
import uvicorn

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from src.db import DatabaseManager
from src.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    print("Starting lifespan")
    db_manager = DatabaseManager()
    print("Connecting to database")
    db_manager.connect()
    # Optionally keep one connection handy as a simple session
    session = db_manager.acquire()
    print("Acquired session")

    app.state.db_manager = db_manager
    app.state.session = session
    try:
        yield
    finally:
        # Release the session connection and close the pool on shutdown
        try:
            if getattr(app.state, "db_manager", None) is not None and getattr(app.state, "session", None) is not None:
                app.state.db_manager.release(app.state.session)
        finally:
            if getattr(app.state, "db_manager", None) is not None:
                app.state.db_manager.close()


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

