from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository
from ..models import Outbox
from ..enums.outbox import EventTypeEnum


class OutboxRepository(BaseRepository[Outbox]):
    model = Outbox

    async def create(
        self,
        session: AsyncSession,
        event_type: EventTypeEnum,
        payload: dict,
    ) -> None:
        new_outbox = self.model(event_type=event_type, payload=payload)

        session.add(new_outbox)
