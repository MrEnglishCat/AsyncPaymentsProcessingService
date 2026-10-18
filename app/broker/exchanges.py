from faststream.rabbit import RabbitExchange, ExchangeType

from ..config.settings import settings

payments_exchange = RabbitExchange(
    name=settings.rabbit.exchange, type=ExchangeType.DIRECT, durable=True
)
