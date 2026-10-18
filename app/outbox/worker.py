import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outbox import Outbox
from app.repository import OutboxRepository
from app.config.logging import setup_logging
from app.config.settings import settings
from app.dependencies.database import db_helper
from app.broker.publisher import publisher_payment_event

logger = logging.getLogger(__name__)


class OutboxWorker:

    def __init__(self):
        self._outbox_repository = OutboxRepository()
        self._running: bool = False

    async def start(self):
        logger.info("Worker is starting...")
        self._running = True
        while self._running:
            try:
                await self._process_backet()
            except Exception as e:
                logger.error(f"Unexpected error in outbox worker: {e}", exc_info=True)

            await asyncio.sleep(settings.outbox.POLL_INTERVAL_SECONDS)

    async def stop(self):
        logger.info(f"Stopping OutboxWorker...")
        self._running = False

    async def _process_backet(self):

        async with db_helper.async_session_maker() as session:
            backets = await self._outbox_repository.get_pending_backet(
                session=session,
                limit=settings.outbox.BACKET_SIZE,
                lock_timeout_seconds=settings.outbox.LOCK_TIMEOUT_SECONDS,
            )

            if not backets:
                logger.info("No available backets for processing")
                return

            logger.info(f"Processing {len(backets)} records...")
            for record in backets:
                await self._process_record(session, record)

            await session.commit()
            logger.info(f"Successfully committed transaction")

    async def _process_record(self, session: AsyncSession, record: Outbox):
        try:
            logger.info(
                f"Publishing event: id={record.id},\n\t"
                f"type={record.event_type},\n\t"
                f"attempt={record.attempts + 1}\n"
            )

            await publisher_payment_event(
                event_type=record.event_type,
                payment_id=record.payload,
                payload=record.payload,
            )

            await self._outbox_repository.mark_as_send(session, record.id)
            logger.info(f"Event published successfully: id={record.id}")
        except Exception as e:

            logger.error(f"Failed to publish event: id={record.id}, error={e}")
            new_attempt = record.attempts + 1

            if new_attempt > settings.outbox.MAX_DELIVERY_ATTEMPTS:
                await self._outbox_repository.mark_as_failed(
                    session,
                    record.id,
                    error_message=str(e),
                )
                logger.error(
                    f"Event permanently failed after {new_attempt} attempts: "
                    f"id={record.id}"
                )
            else:
                await self._outbox_repository.record_retry(
                    session, record.id, str(e), new_attempt
                )
                logger.warning(
                    f"Event will retry: id={record.id}, "
                    f"attempts={new_attempt}/{settings.outbox.MAX_DELIVERY_ATTEMPTS}"
                )


async def main():
    setup_logging(log_file="./logs/logging.txt")

    worker = OutboxWorker()
    try:
        t1 = asyncio.create_task(worker.start())
        await t1
    finally:
        await worker.stop()
        t1.cancel()
        await asyncio.sleep(4)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
