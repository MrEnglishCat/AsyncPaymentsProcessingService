from uuid import UUID
from datetime import datetime, UTC

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.payments import PaymentCreateSchema
from .base import BaseRepository
from ..models import Payment
from ..enums.payment import PaymentStatusEnum


class PaymentRepository(BaseRepository[Payment]):
    model = Payment

    async def create(self, session: AsyncSession, payment: PaymentCreateSchema) -> UUID:
        new_payment = self.model(**payment.model_dump())
        session.add(new_payment)
        await session.flush()
        return new_payment

    async def get_by_idempotency_key(
        self, session: AsyncSession, idempotency_key: UUID
    ) -> Payment:
        payment = await session.scalar(
            select(self.model).where(self.model.idempotency_key == idempotency_key)
        )
        return payment

    async def update_status(
        self,
        session: AsyncSession,
        payment_id: UUID,
        new_status: PaymentStatusEnum,
    ) -> None:
        await session.execute(
            update(Payment)
            .where(Payment.id == payment_id)
            .values(
                status=new_status,
                processed_at=datetime.now(UTC),
            )
        )
