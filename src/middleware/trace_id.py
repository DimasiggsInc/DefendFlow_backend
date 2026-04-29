import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class TraceIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Trace-ID", f"req_{uuid.uuid4().hex[:12]}")
        request.state.trace_id = trace_id
        response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id
        return response
