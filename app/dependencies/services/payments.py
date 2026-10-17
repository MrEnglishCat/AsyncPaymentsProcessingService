from typing import Annotated
from uuid import uuid4

from fastapi import Depends

from ...repository import PaymentRepository
from ...services import PaymentService
from ...schemas import PaymentCreateSchema, PaymentPayloadSchema
from ..base import get_header_dependency


def get_payment_repository() -> PaymentRepository:
    return PaymentRepository()


def get_payment_service(
    repository: PaymentRepository = Depends(get_payment_repository),
) -> PaymentService:
    return PaymentService(repository=repository)


def generate_body(
    idempotency_key: Annotated[
        str,
        Depends(
            get_header_dependency("Idempotency-Key", description=f"For copy: {uuid4()}")
        ),
    ],
    payload: PaymentPayloadSchema,
) -> PaymentCreateSchema:
    return PaymentCreateSchema(
        **payload.model_dump(),
        idempotency_key=idempotency_key,
    )
