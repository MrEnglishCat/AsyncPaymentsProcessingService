import asyncio
import logging

from datetime import datetime, UTC
import aiohttp
from typing import Any

from ..config.settings import settings

logger = logging.getLogger(__name__)


class WebhookService:

    def __init__(self):
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=settings.webhook.WEBHOOK_TIMEOUT)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def send_with_retry(
        self, webhook_url: str, payment_data: dict[str, Any]
    ) -> bool:
        payload = {
            "event": "payment.status_changed",
            "processed_at": datetime.now(UTC).isoformat(),
            "data": payment_data,
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AsyncPayments-Webhook/1.0",
            "X-Webhook-Event": "payment.status_changed",
        }

        async_client = await self._get_session()

        for attempt, delay in enumerate(settings.webhook.RETRY_DELAYS, start=1):
            try:
                logger.info(f"Sending webhook to {webhook_url} (attempt {attempt}/3)")

                async with async_client.post(
                    webhook_url,
                    json=payload,
                    headers=headers,
                ) as response:

                    if 200 <= response.status <= 300:
                        response_json = await response.json()
                        logger.info(
                            f"Webhook delivered successfully to {webhook_url}\n\t{response_json}"
                        )
                        return True

                    if 400 <= response.status < 500:
                        logger.warning(
                            f"Webhook rejected by client (4xx): {response.status}"
                        )
                        return False

                    logger.warning(
                        f"Webhook failed with status {response.status}, "
                        f"retrying in {delay}s..."
                    )

            except asyncio.TimeoutError:
                logger.warning(f"Webhook connection timed out, retrying in {delay}s...")
            except aiohttp.ClientConnectorError as e:
                logger.warning(
                    f"Webhook connection error ({e.__class__.__name__}), "
                    f"retrying in {delay}s..."
                )
            except aiohttp.ClientError as e:
                logger.error(f"Unexpected aiohttp client error: {e}")
                return False
            except Exception as e:
                logger.error(f"Unexpected webhook error: {e}")
                return False

            if attempt < len(settings.webhook.RETRY_DELAYS):
                await asyncio.sleep(delay)

        logger.error(f"Webhook permanently failed after 3 attempts to {webhook_url}")
        return False


webhook_service = WebhookService()
