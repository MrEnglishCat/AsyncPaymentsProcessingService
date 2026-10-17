from fastapi import Depends

from ...repository.outbox import OutboxRepository
from ...services import OutboxService


def get_outbox_repository() -> OutboxRepository:
    return OutboxRepository()


def get_outbox_service(
    repository: OutboxRepository = Depends(get_outbox_repository),
) -> OutboxService:
    return OutboxService(
        repository=repository,
    )
