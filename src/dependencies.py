from fastapi import Request

async def get_redis(request: Request):
    yield request.app.state.redis
