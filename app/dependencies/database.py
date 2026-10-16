from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from ..config.settings import settings


class DatabaseHelper:
    def __init__(
        self,
        url: str,
        echo: bool = False,
        echo_pool: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ):
        self.async_engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
        )

        self.async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            expire_on_commit=settings.db.expire_on_commit,
            autocommit=settings.db.autocommit,
            autoflush=settings.db.autoflush,
            pool_size=pool_size,
            max_over_flow=max_overflow,
        )

    async def dispose(self) -> None:
        await self.async_engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.async_session_maker() as session:
            yield session


db_helper = DatabaseHelper(
    url=settings.db.DB_URL,
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_over_flow,
)
