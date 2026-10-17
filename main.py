import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.main_router import api_router
from app.config.settings import settings
from app.dependencies.database import db_helper
from app.exceptions.handlers import setup_exception_handlers
from app.config.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:

        yield
    finally:
        await db_helper.dispose()


setup_logging(log_file="./logs/logging.txt")

apps = FastAPI(lifespan=lifespan)
apps.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="session",
    max_age=86400 * 7,
)
apps.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_exception_handlers(apps)

apps.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(
        app="main:apps",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
    )
