import uuid

from alembic.util import status
from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession


from exceptions import AppException
from src.config import settings
from src.auth.router import router as auth_router
from src.projects.router import router as projects_router

from src.database import get_session


from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.redis import init_redis, close_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis(app)
    yield
    await close_redis(app)

app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def root():
    """Эндпоинт для проверки состояния сервера."""
    return {"status": "ok", "version": settings.APP_VERSION}



# for router in routers:
#     app.include_router(router, prefix="/api/v1")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(projects_router, prefix="/api/v1")


# Middleware для trace_id
class TraceIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Trace-ID", f"req_{uuid.uuid4().hex[:12]}")
        request.state.trace_id = trace_id
        response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id
        return response

app.add_middleware(TraceIDMiddleware)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        errors.append({
            "field": ".".join(map(str, err.get("loc", []))),
            "message": err.get("msg"),
            "type": err.get("type")
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": errors,
                "trace_id": getattr(request.state, "trace_id", None)
            }
        },
    )

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "trace_id": getattr(request.state, "trace_id", None)
            }
        },
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    detail = str(exc) if settings.DEBUG else "Internal server error"
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": detail,
                "details": None,
                "trace_id": getattr(request.state, "trace_id", None)
            }
        },
    )




if __name__ == "__main__":
    import uvicorn

    server_port = settings.PORT
    uvicorn.run("app:app", host="0.0.0.0", port=server_port, reload=True)
