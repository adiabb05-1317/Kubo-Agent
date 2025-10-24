from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .settings import settings


class Base(AsyncAttrs, DeclarativeBase):
    pass


engine: AsyncEngine = create_async_engine(settings.database_url, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    session = SessionLocal()
    try:
        yield session
    finally:
        await session.close()


async def init_models(metadata_only: bool = False) -> None:
    # Import models to ensure they are registered with Base.metadata
    from . import models  # noqa: F401

    async with engine.begin() as conn:
        if metadata_only:
            await conn.run_sync(Base.metadata.create_all)
        else:
            await conn.run_sync(Base.metadata.create_all)


def run_sync(coro) -> None:
    try:
        asyncio.run(coro)
    except RuntimeError:
        # If already in an event loop (e.g., uvicorn), schedule it
        loop = asyncio.get_event_loop()
        loop.create_task(coro)


