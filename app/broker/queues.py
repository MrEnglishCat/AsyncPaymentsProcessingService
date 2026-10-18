from faststream.rabbit import RabbitQueue

from ..config.settings import settings

payment_new_queue = RabbitQueue(
    name=settings.rabbit.queue_new,
    durable=True,
    arguments={
        "x-dead-letter-exchange": "",
        "x-dead-letter-routing-key": settings.rabbit.queue_dlq,
    },
    routing_key=settings.rabbit.queue_new,
)

payment_dlq_queue = RabbitQueue(name=settings.rabbit.queue_dlq, durable=True)
