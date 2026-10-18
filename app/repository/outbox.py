from uuid import UUID
from datetime import datetime, UTC, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository
from ..models import Outbox
from ..enums.outbox import EventTypeEnum, OutboxStatusEnum
from ..config.settings import settings


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

    async def get_pending_backet(
        self, session: AsyncSession, limit: int, lock_timeout_seconds: int
    ) -> list[Outbox]:
        now = datetime.now(UTC)
        locked_time = now + timedelta(lock_timeout_seconds)

        stmt = (
            select(self.model)
            .where(
                (self.model.status == OutboxStatusEnum.PENDING)
                | (self.model.status != OutboxStatusEnum.PROCESSING)
                & (self.model.locked_until < now)
            )
            .order_by(self.model.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        records = await session.scalars(stmt).all()
        if records:
            records_ids = [record.id for record in records]
            stmt = (
                update(self.model)
                .where(self.model.id.in_(records_ids))
                .values(locked_time=locked_time, status=OutboxStatusEnum.PROCESSING)
            )
            await session.execute(stmt)
            await session.flush()

        return records

    async def mark_as_send(self, session: AsyncSession, pk: UUID) -> None:
        stmt = (
            update(self.model)
            .where(self.model.id == pk)
            .values(
                status=OutboxStatusEnum.SENT,
                processed_at=datetime.now(UTC),
                locked_until=None,
                error_message=None,
            )
        )
        await session.execute(stmt)
        await session.commit()

    async def mark_as_permanently_failed(
        self,
        session: AsyncSession,
        outbox_id: UUID,
        error_message: str,
    ) -> None:
        await session.execute(
            update(Outbox)
            .where(Outbox.id == outbox_id)
            .values(
                status=OutboxStatusEnum.FAILED,
                attempts=Outbox.attempts + 1,
                error_message=error_message[:1000],
                processed_at=datetime.now(UTC),
                locked_until=None,
            )
        )

    async def record_retry(
        self, session: AsyncSession, outbox_id: UUID, error_message: str, attempts: int
    ) -> None:
        await session.execute(
            update(Outbox)
            .where(Outbox.id == outbox_id)
            .values(
                status=OutboxStatusEnum.PENDING,
                attempts=attempts,
                error_message=error_message[:1000],
                processed_at=datetime.now(UTC),
                locked_until=None,
            )
        )
