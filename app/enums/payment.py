from enum import StrEnum

__all__ = (
    "PaymentStatusEnum",
    "CurrencyEnum",
)


class PaymentStatusEnum(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class CurrencyEnum(StrEnum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"
