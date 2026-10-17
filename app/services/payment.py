import logging
from uuid import UUID
from typing import Type

from fastapi import status, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import (
    PaymentCreateSchema,
    PaymentReadSchema,
    PaymentCreateResponseSchema,
)
from ..repository import PaymentRepository

logger = logging.getLogger(__name__)


class PaymentService:

    def __init__(self, repository: PaymentRepository):
        self._repository: PaymentRepository = repository

    async def get_all(self, session: AsyncSession) -> list[PaymentReadSchema]:
        return await self._repository.get_all(session)

    async def get_by_idempotency_key(
        self, session: AsyncSession, idempotency_key: UUID
    ) -> PaymentReadSchema:
        return await self._repository.get_by_idempotency_key(session, idempotency_key)

    async def get(self, session: AsyncSession, uuid: UUID) -> PaymentReadSchema | None:
        return await self._repository.get(session, pk=uuid)

    async def create(
        self, session: AsyncSession, payment: PaymentCreateSchema
    ) -> PaymentCreateResponseSchema:
        try:
            new_payment = await self._repository.create(session, payment)
            await session.commit()
            return PaymentCreateResponseSchema.model_validate(new_payment)
        except IntegrityError as e:
            await session.rollback()
            if "idempotency_key" in str(e):
                existing_payment = await self._repository.get_by_idempotency_key(
                    session, payment.idempotency_key
                )
                if (
                    existing_payment.amount != payment.amount
                    or existing_payment.currency != payment.currency
                    or existing_payment.webhook_url != payment.webhook_url
                ):
                    logger.warning(
                        f"The Idempotency-Key has already been used with different payment data.\n\tInput payment {payment}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="The Idempotency-Key has already been used with different payment data.",
                    )

                return PaymentCreateResponseSchema.model_validate(existing_payment)
            logger.warning(
                f"Unexpected error while creating a payment.\n\tInput payment {payment}\n\tExc:{str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error while creating a payment",
            )
