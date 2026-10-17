from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.payments import PaymentCreateSchema
from .base import BaseRepository
from ..models import Payment


class PaymentRepository(BaseRepository[Payment]):
    model = Payment

    async def create(self, session: AsyncSession, payment: PaymentCreateSchema) -> UUID:
        new_payment = self.model(**payment.model_dump())
        session.add(new_payment)
        session.refresh(new_payment)
        return new_payment

    async def get_by_idempotency_key(
        self, session: AsyncSession, idempotency_key: UUID
    ) -> Payment:
        payment = await session.scalar(
            select(self.model).where(self.model.idempotency_key == idempotency_key)
        )
        return payment
