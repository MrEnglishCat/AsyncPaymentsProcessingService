import logging

from fastapi import HTTPException, Request, FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from .exceptions import (
    IdempotencyKeyException,
    NotFoundItemException,
    RequestValidationException,
)
from ..utils.response import ResponseFactory

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI):

    def __generate_log_message(exc: Exception, request: Request):
        return f"{exc.__class__.__name__} on {request.method} {request.url}.\n\tMessage:{exc.detail}"

    @app.exception_handler(NotFoundItemException)
    async def not_found_item_error_handler(
        request: Request, exc: NotFoundItemException
    ):
        logger.error(__generate_log_message(exc, request))

        return JSONResponse(
            status_code=exc.status_code,
            content=ResponseFactory.ok(message=exc.detail, as_dict=True),
        )

    @app.exception_handler(IdempotencyKeyException)
    async def idempotency_key_error_handler(
        request: Request, exc: IdempotencyKeyException
    ):
        logger.error(__generate_log_message(exc, request))

        return JSONResponse(
            status_code=exc.status_code,
            content=ResponseFactory.error(
                message="Duplicate idempotency key",
                errors=[{"field": "idempotency_key", "message": "Key already exists"}],
                as_dict=True,
            ),
        )

    @app.exception_handler(HTTPException)
    @app.exception_handler(IntegrityError)
    @app.exception_handler(RequestValidationException)
    async def default_error_handler(
        request: Request,
        exc: IntegrityError | RequestValidationException | IntegrityError,
    ):
        logger.error(__generate_log_message(exc, request))
        return JSONResponse(
            status_code=exc.status_code,
            content=ResponseFactory.error(message=exc.detail, as_dict=True),
        )
