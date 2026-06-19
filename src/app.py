from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.middleware.rate_limiter import setup_rate_limit_middleware
from src.middleware.trace_id import TraceIDMiddleware
from src.exceptions import AppException
from src.config import settings
from src.auth.router import router as auth_router
from src.projects.router import router as projects_router
from src.users.router import router as user_router

from src.protocols.router import grades_router, protocols_router, final_score_router
from src.defense.router import rooms_router, slots_router
from src.registrations.router import registrations_expert_router, registrations_student_router


from contextlib import asynccontextmanager
from src.redis import init_redis, close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis(app)
    yield
    await close_redis(app)

app = FastAPI(lifespan=lifespan)


app.mount("/static", StaticFiles(directory="static"), name="static")

setup_rate_limit_middleware(app)
app.add_middleware(TraceIDMiddleware)  # Middleware для trace_id


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health_check():
    """Эндпоинт для проверки состояния сервера."""
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/", tags=["root"])
async def root(request: Request):
    return {"message": "Welcome to the DefendFlow API!"}


# for router in routers:
#     app.include_router(router, prefix="/api/v1")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(projects_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")

app.include_router(registrations_expert_router, prefix="/api/v1")
app.include_router(registrations_student_router, prefix="/api/v1")

app.include_router(rooms_router, prefix="/api/v1")
app.include_router(slots_router, prefix="/api/v1")
app.include_router(grades_router, prefix="/api/v1")
app.include_router(protocols_router, prefix="/api/v1")
app.include_router(final_score_router, prefix="/api/v1")



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
    detail = "Internal server error"
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
