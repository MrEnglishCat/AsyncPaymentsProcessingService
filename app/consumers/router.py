import json
import logging
import random
import asyncio
from uuid import UUID

from faststream.rabbit import RabbitRouter, RabbitMessage

from ..broker import payment_new_queue, payments_exchange
from ..dependencies.database import db_helper
from ..repository import PaymentRepository
from ..services import webhook_service

logger = logging.getLogger(__name__)

consumer_router = RabbitRouter()
payment_repo = PaymentRepository()


@consumer_router.subscriber(
    queue=payment_new_queue,
    exchange=payments_exchange,
)
async def process_payment_event(
    message: RabbitMessage,
):
    payment_id_str = message.message_id
    message = json.loads(message.body.decode())
    webhook_url = message["webhook_url"]

    if not payment_id_str or not webhook_url:
        logger.error(f"Invalid message payload: {message}")
        return

    payment_id = UUID(payment_id_str)
    logger.info(f"Started processing payment: {payment_id}")
    async with db_helper.async_session_maker() as session:

        try:
            processing_time = random.uniform(2.0, 5.0)
            await asyncio.sleep(processing_time)

            is_success = random.random() <= 0.90
            new_status = "succeeded" if is_success else "failed"

            logger.info(
                f"Payment {payment_id} processing finished with status: {new_status}"
            )

            await payment_repo.update_status(session, payment_id, new_status)
            await session.commit()
            logger.info(f"Payment {payment_id} status updated in DB")

            webhook_success = await webhook_service.send_with_retry(
                webhook_url=webhook_url,
                payment_data={
                    "id": payment_id_str,
                    "status": new_status,
                    "amount": message.get("amount"),
                    "currency": message.get("currency"),
                },
            )

            if not webhook_success:
                logger.error(
                    f"Webhook delivery failed for payment {payment_id}. "
                    "Raising exception to trigger DLQ."
                )
                raise Exception("Webhook delivery failed after 3 attempts")

            logger.info(f"Successfully finished processing payment: {payment_id}")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error processing payment {payment_id}: {e}")
            raise
