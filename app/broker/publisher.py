from typing import Any
from uuid import UUID


from .broker import broker
from .exchanges import payments_exchange
from ..enums.outbox import EventTypeEnum
from ..config.settings import settings


async def publisher_payment_event(
    event_type: EventTypeEnum,
    payload: dict[str, Any],
    payment_id: UUID,
) -> None:
    await broker.publish(
        message=payload,
        exchange=payments_exchange,
        routing_key=settings.rabbit.queue_new,
        message_id=payment_id,
        headers={"event_type": event_type},
        content_type="application/json",
    )
