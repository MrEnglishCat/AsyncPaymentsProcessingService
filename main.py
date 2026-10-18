import uvicorn
import logging
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.main_router import api_router
from app.config.settings import settings
from app.dependencies.database import db_helper
from app.exceptions.handlers import setup_exception_handlers
from app.config.logging import setup_logging
from app.broker import faststream_app, setup_broker_routers
from app.outbox.producer import OutboxProducer

logger = logging.getLogger(__name__)
outbox_worker = OutboxProducer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting APPS...")
        logger.info("Starting RabbitMQ broker...")
        setup_broker_routers()
        await faststream_app.start()
        logger.info("RabbitMQ broker started")

        logger.info("Starting OutboxWorker...")
        outbox_task = asyncio.create_task(outbox_worker.start())
        yield
        logger.info("Stopping APPS...")
        logger.info("Stopping OutboxWorker...")
        await outbox_worker.stop()
        outbox_task.cancel()

    finally:
        await db_helper.dispose()
        logger.info("RabbitMQ broker will stopping")
        await faststream_app.stop()

        logger.info("all services is stop")


setup_logging(log_file="./logs/logging.txt")

apps = FastAPI(
    title="Async Payments Processing Service",
    lifespan=lifespan,
)
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
