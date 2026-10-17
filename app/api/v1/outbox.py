from uuid import UUID

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.settings import settings
from ...dependencies.database import db_helper
from ...dependencies.services import get_outbox_service
from ...services import OutboxService
from ...schemas import OutboxReadSchema
from ...utils.response import BaseResponse, ResponseFactory

outbox_router = APIRouter(prefix=settings.api.v1.outbox)


@outbox_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[list[OutboxReadSchema]],
    summary="View the full Outbox list",
)
async def get_all_outbox(
    session: AsyncSession = Depends(db_helper.session_getter),
    service: OutboxService = Depends(get_outbox_service),
):

    outboxes = await service.get_all(session)
    return ResponseFactory.ok(data=outboxes)


@outbox_router.get(
    "/{outbox_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[OutboxReadSchema],
    summary="View the one message from Outbox list",
)
async def get_outbox_by_id(
    outbox_id: UUID = Path(description="Unique payment identifier"),
    session: AsyncSession = Depends(db_helper.session_getter),
    service: OutboxService = Depends(get_outbox_service),
):

    outboxes = await service.get(session, outbox_id)
    return ResponseFactory.ok(data=outboxes)
