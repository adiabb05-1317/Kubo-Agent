from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, Optional
import psycopg2  # type: ignore
from psycopg2.pool import SimpleConnectionPool 
from .settings import settings


class DatabaseManager:
    """Lightweight connection pool manager using psycopg2.

    Provides a simple sync pool for direct SQL needs.
    """

    def __init__(self, dsn: Optional[str] = None, minconn: int = 1, maxconn: int = 5) -> None:
        # DSN from settings if not provided
        self.dsn: str = dsn or settings.database_url
        self.minconn = minconn
        self.maxconn = maxconn
        self._pool: Optional[SimpleConnectionPool] = None

    def connect(self) -> None:
        if self._pool is None:
            self._pool = SimpleConnectionPool(self.minconn, self.maxconn, dsn=self.dsn)

    def close(self) -> None:
        if self._pool is not None:
            self._pool.closeall()
            self._pool = None

    def acquire(self):
        if self._pool is None:
            raise RuntimeError("DatabaseManager pool is not initialized. Call connect() first.")
        return self._pool.getconn()

    def release(self, conn) -> None:
        if self._pool is not None and conn is not None:
            self._pool.putconn(conn)

    @contextmanager
    def connection(self) -> Generator:
        conn = None
        try:
            conn = self.acquire()
            yield conn
        finally:
            if conn is not None:
                self.release(conn)

    @contextmanager
    def cursor(self) -> Generator:
        with self.connection() as conn:
            cur = conn.cursor()
            try:
                yield cur
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                cur.close()



