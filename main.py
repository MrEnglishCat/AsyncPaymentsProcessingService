import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
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
setup_exception_handlers(apps)

apps.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(
        app="main:apps",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
    )
