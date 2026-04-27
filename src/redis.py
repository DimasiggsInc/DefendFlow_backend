# src/redis.py
import redis.asyncio as aioredis
from fastapi import FastAPI
from src.config import settings

async def init_redis(app: FastAPI) -> None:
    app.state.redis = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=settings.REDIS_MAX_CONNECTIONS,
        retry_on_timeout=True,
    )

async def close_redis(app: FastAPI) -> None:
    await app.state.redis.aclose()
