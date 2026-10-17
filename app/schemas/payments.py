from datetime import datetime
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field

from ..enums import CurrencyEnum, PaymentStatusEnum
from .base import IDSchema


class PaymentSchema(BaseModel):
    amount: Decimal = Field(max_digits=19, decimal_places=4)
    currency: CurrencyEnum
    description: str = Field(max_length=500)
    meta: dict = Field(default_factory=dict)
    webhook_url: str = Field(max_length=500)


class PaymentPayloadSchema(PaymentSchema): ...


class PaymentCreateSchema(PaymentSchema):
    idempotency_key: UUID | None = Field(default=None)


class PaymentReadSchema(IDSchema, PaymentSchema):
    status: PaymentStatusEnum = Field(default=PaymentStatusEnum.PENDING)
    processed_at: datetime | None
    created_at: datetime
    idempotency_key: UUID


class PaymentCreateResponseSchema(IDSchema):
    status: PaymentStatusEnum = Field(default=PaymentStatusEnum.PENDING)
    created_at: datetime
