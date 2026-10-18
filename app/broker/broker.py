from faststream.rabbit import RabbitBroker


from ..config.settings import settings

broker = RabbitBroker(
    settings.rabbit.URL,
)


def setup_broker_routers() -> None:
    from app.consumers.router import consumer_router

    broker.include_router(consumer_router)
