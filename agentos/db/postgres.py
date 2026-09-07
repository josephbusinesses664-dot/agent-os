"""PostgreSQL-backed repository and Redis-backed KV/queue.

Postgres stores every aggregate as a row of (collection, key, data JSONB).
Redis is used for the task queue, caching and counters when configured.
"""

from __future__ import annotations

import json
from typing import Any, Optional

from sqlalchemy import JSON, BigInteger, Column, DateTime, Index, String, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .base import KVStore, Queue, Repository


class Base(DeclarativeBase):
    pass


class DocRow(Base):
    __tablename__ = "agentos_docs"
    collection = Column(String(64), primary_key=True)
    key = Column(String(128), primary_key=True)
    data = Column(JSON, nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)


Index("ix_agentos_docs_updated", DocRow.updated_at)


class PostgresRepository(Repository):
    """JSONB document store over PostgreSQL."""

    def __init__(self, database_url: str) -> None:
        self.engine = create_async_engine(database_url, pool_pre_ping=True)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def init(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        await self.engine.dispose()

    async def put(self, collection: str, key: str, doc: dict) -> None:
        async with self.session_factory() as session:
            row = await session.get(DocRow, (collection, key))
            if row is None:
                session.add(
                    DocRow(collection=collection, key=key, data=doc, updated_at=func.now())
                )
            else:
                row.data = doc
                row.updated_at = func.now()
            await session.commit()

    async def get(self, collection: str, key: str) -> Optional[dict]:
        async with self.session_factory() as session:
            row = await session.get(DocRow, (collection, key))
            return dict(row.data) if row else None

    async def delete(self, collection: str, key: str) -> None:
        async with self.session_factory() as session:
            row = await session.get(DocRow, (collection, key))
            if row:
                await session.delete(row)
                await session.commit()

    async def query(self, collection: str, predicate: Optional[dict] = None) -> list[dict]:
        predicate = predicate or {}
        async with self.session_factory() as session:
            stmt = select(DocRow).where(DocRow.collection == collection)
            rows = (await session.execute(stmt)).scalars().all()
        docs = [dict(r.data) for r in rows]
        if predicate:
            docs = [d for d in docs if all(d.get(k) == v for k, v in predicate.items())]
        return docs

    async def count(self, collection: str, predicate: Optional[dict] = None) -> int:
        return len(await self.query(collection, predicate))

    async def health(self) -> bool:
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False


class RedisKV(KVStore):
    def __init__(self, redis_url: str) -> None:
        import redis.asyncio as aioredis

        self._redis = aioredis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str) -> Optional[str]:
        return await self._redis.get(key)

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        await self._redis.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)

    async def incr(self, key: str, amount: int = 1) -> int:
        return await self._redis.incrby(key, amount)

    async def expire(self, key: str, ttl: int) -> None:
        await self._redis.expire(key, ttl)

    async def health(self) -> bool:
        try:
            return bool(await self._redis.ping())
        except Exception:
            return False


class RedisQueue(Queue):
    def __init__(self, redis_url: str, queue_name: str = "agentos:tasks") -> None:
        import redis.asyncio as aioredis

        self._redis = aioredis.from_url(redis_url, decode_responses=True)
        self._queue = queue_name

    async def enqueue(self, item: dict) -> None:
        await self._redis.lpush(self._queue, json.dumps(item))

    async def dequeue(self, timeout: float = 1.0) -> Optional[dict]:
        raw = await self._redis.brpop(self._queue, timeout=timeout)
        if not raw:
            return None
        return json.loads(raw[1])

    async def size(self) -> int:
        return int(await self._redis.llen(self._queue))

    async def health(self) -> bool:
        try:
            return bool(await self._redis.ping())
        except Exception:
            return False