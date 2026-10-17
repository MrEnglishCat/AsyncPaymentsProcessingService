from uuid import UUID

from fastapi import APIRouter, Depends, status, Path
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ...exceptions.exceptions import NotFoundItemException
from ...enums import PaymentStatusEnum
from ...schemas import (
    PaymentReadSchema,
    PaymentCreateSchema,
    PaymentCreateResponseSchema,
)
from ...config.settings import settings
from ...dependencies.database import db_helper
from ...utils.response import ResponseFactory, BaseResponse
from ...services import PaymentService
from ...dependencies.services import get_payment_service, generate_body

payments_router = APIRouter(prefix=settings.api.v1.payments)


@payments_router.post(
    "/",
    response_model=BaseResponse[PaymentCreateResponseSchema],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create payment",
)
async def create_payment(
    payment: PaymentCreateSchema = Depends(generate_body),
    session: AsyncSession = Depends(db_helper.session_getter),
    service: PaymentService = Depends(get_payment_service),
):

    payment_create = await service.create(session, payment)
    if payment_create.status == PaymentStatusEnum.PENDING:
        status_code = status.HTTP_202_ACCEPTED
    elif payment_create.status == PaymentStatusEnum.SUCCEEDED:
        status_code = status.HTTP_200_OK

    return JSONResponse(
        status_code=status_code,
        content=ResponseFactory.ok(data=payment_create, as_dict=True, mode="json"),
    )


@payments_router.get(
    "/",
    response_model=BaseResponse[list[PaymentReadSchema]],
    status_code=status.HTTP_200_OK,
    summary="Get all payments",
)
async def get_all_payments(
    session: AsyncSession = Depends(db_helper.session_getter),
    service: PaymentService = Depends(get_payment_service),
):
    response_data = await service.get_all(session)
    return ResponseFactory.ok(data=response_data)


@payments_router.get(
    "/{payment_id}",
    response_model=BaseResponse[PaymentReadSchema],
    status_code=status.HTTP_200_OK,
    summary="Get one payment",
)
async def get_payment_by_id(
    payment_id: UUID = Path(description="Unique payment identifier"),
    session: AsyncSession = Depends(db_helper.session_getter),
    service: PaymentService = Depends(get_payment_service),
):
    payment = await service.get(session, payment_id)
    if payment is None:
        raise NotFoundItemException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with ID {payment_id} not found",
        )
    return ResponseFactory.ok(data=payment)
