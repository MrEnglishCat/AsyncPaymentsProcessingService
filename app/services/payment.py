import logging
from uuid import UUID

from fastapi import status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import (
    PaymentCreateSchema,
    PaymentReadSchema,
    PaymentCreateResponseSchema,
)
from ..exceptions.exceptions import ConflictItemsException, AppBaseException
from ..repository import PaymentRepository, OutboxRepository
from ..enums.outbox import EventTypeEnum

logger = logging.getLogger(__name__)


class PaymentService:

    def __init__(
        self, repository: PaymentRepository, outbox_repository: OutboxRepository
    ):
        self._repository: PaymentRepository = repository
        self._outbox_repository: OutboxRepository = outbox_repository

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
            await self._outbox_repository.create(
                session=session,
                event_type=EventTypeEnum.PAYMENT_CREATED,
                payload={
                    "payment_id": str(new_payment.id),
                    "amount": str(new_payment.amount),
                    "currency": new_payment.currency,
                    "status": new_payment.status,
                    "webhook_url": new_payment.webhook_url,
                },
            )
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
                    raise ConflictItemsException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="The Idempotency-Key has already been used with different payment data.",
                    )

                return PaymentCreateResponseSchema.model_validate(existing_payment)

            logger.error(
                f"Unexpected error while creating a payment.\n\tInput payment {payment}\n\tExc:{str(e)}"
            )
            raise AppBaseException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error while creating a payment",
            )
