from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..repository import OutboxRepository
from ..schemas import OutboxReadSchema


class OutboxService:

    def __init__(self, repository: OutboxRepository):
        self._repository = repository

    async def get_all(self, session: AsyncSession) -> list[OutboxReadSchema]:
        return await self._repository.get_all(session)

    async def get(self, session: AsyncSession, uuid: UUID) -> OutboxReadSchema | None:
        return await self._repository.get(session, pk=uuid)
