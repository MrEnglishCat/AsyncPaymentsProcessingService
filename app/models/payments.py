from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SA_Enum,
    String,
    UUID as SA_UUID,
    Numeric,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from ..models.base import BaseAlchemyModel
from .mixins import UUIDMixin, TimestampMixin
from ..enums import CurrencyEnum, PaymentStatusEnum
from ..config.settings import settings


class Payment(
    BaseAlchemyModel,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_payment_amount_positive"),
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4))
    currency: Mapped[CurrencyEnum] = mapped_column(
        SA_Enum(
            CurrencyEnum,
            name="currency",
            create_type=False,
            native_enum=True,
        )
    )
    description: Mapped[str] = mapped_column(String(500))
    meta: Mapped[dict] = mapped_column(JSONB, default=dict)
    status: Mapped[PaymentStatusEnum] = mapped_column(
        SA_Enum(
            PaymentStatusEnum,
            name="payments",
            create_type=False,
            native_enum=True,
        ),
        default=PaymentStatusEnum.PENDING,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    idempotency_key: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid=True), default=uuid4, unique=True, index=True
    )
    webhook_url: Mapped[str] = mapped_column(
        String(500), default=settings.webhook.WEBHOOK_URL
    )
