from logging import getLogger

import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.main_router import api_router
from app.config.settings import settings
from app.dependencies.database import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await db_helper.dispose()


main_logger = getLogger(__name__)
apps = FastAPI(lifespan=lifespan)
apps.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(
        app="main:apps",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
    )
