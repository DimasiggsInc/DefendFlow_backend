from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.ext.asyncio import AsyncSession


from src.config import settings
from src.auth.router import router as auth_router
from src.projects.router import router as projects_router

from src.database import get_session


app = FastAPI()

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




if __name__ == "__main__":
    import uvicorn

    server_port = settings.PORT
    uvicorn.run("app:app", host="0.0.0.0", port=server_port, reload=True)
