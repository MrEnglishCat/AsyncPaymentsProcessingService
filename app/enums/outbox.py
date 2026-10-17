from enum import StrEnum


class OutboxStatusEnum(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"
    EXPIRED = "expired"


class EventTypeEnum(StrEnum):
    PAYMENT_CREATED = "payment.created"
    PAYMENT_STATUS_CHANGED = "payment.status_changed"
