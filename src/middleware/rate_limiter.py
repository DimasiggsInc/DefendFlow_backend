# src/middleware/rate_limiter.py
from fastapi import Request, FastAPI
from cashews import cache

from src.config import settings
# RATE_LIMIT = 100
# WINDOW = 1
# BAN_DURATION = 300


cache.setup("redis://redis:6379")


def setup_rate_limit_middleware(app: FastAPI):
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        client_ip = _get_client_ip(request)
        
        # Проверяем бан
        if await cache.get(f"ban:{client_ip}"):
            return _json_response(
                status_code=429,
                detail="IP temporarily banned"
            )
        
        # Проверяем лимит
        if not await _check_rate_limit(client_ip):
            await cache.set(f"ban:{client_ip}", "1", expire=settings.BAN_DURATION)
            return _json_response(
                status_code=429,
                detail="Rate limit exceeded. Try later."
            )
        
        # Всё ок — передаём запрос дальше
        return await call_next(request)
    
    return rate_limit_middleware


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def _check_rate_limit(ip: str) -> bool:
    """Fixed window counter через cashews"""
    key = f"rate:{ip}"
    current = await cache.get(key)
    
    if current is None:
        await cache.set(key, 1, expire=settings.WINDOW)
        return True
    
    new_count = await cache.incr(key)
    if new_count == 1:  # edge case: ключ экспайрился между get и incr
        await cache.expire(key, settings.WINDOW)
    
    return new_count <= settings.RATE_LIMIT_COUNT


def _json_response(status_code: int, detail: str):
    """Возвращаем JSON-ответ без выброса исключения"""
    from starlette.responses import JSONResponse
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail}
    )
