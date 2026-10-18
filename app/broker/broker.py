from faststream.rabbit import RabbitBroker
from faststream import FastStream

from ..config.settings import settings
from .exchanges import payments_exchange
from .queues import payment_new_queue, payment_dlq_queue

broker = RabbitBroker(
    settings.rabbit.URL,
)
faststream_app = FastStream(broker)


@faststream_app.after_startup
async def declare():

    new_queue = await broker.declare_queue(payment_new_queue)
    await broker.declare_queue(payment_dlq_queue)
    exchange = await broker.declare_exchange(payments_exchange)
    await new_queue.bind(exchange=exchange)


def setup_broker_routers() -> None:
    from ..consumers.router import consumer_router

    broker.include_router(consumer_router)
