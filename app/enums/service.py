from enum import StrEnum


class ServiceTypeEnum(StrEnum):
    PAYMENTS = "payments"
    OUTBOX = "outbox"
    WEBHOOK = "webhook"
    FAST_STREAM = "fast_stream"
