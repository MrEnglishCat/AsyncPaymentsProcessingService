from uuid import UUID
from typing import Generic, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    model: ModelT

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list[ModelT]:
        payments_coro = await session.scalars(select(cls.model))
        return payments_coro.all()

    @classmethod
    async def get(cls, session: AsyncSession, pk: UUID) -> ModelT | None:
        obj = await session.get(cls.model, pk)
        return obj
