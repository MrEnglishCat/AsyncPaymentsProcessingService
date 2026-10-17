from typing import Any

from fastapi import HTTPException


class BaseCustomException(Exception):
    def __init__(self, status_code: int, detail: Any):
        self.status_code = status_code
        self.detail = detail
        super().__init__()


class AppBaseException(BaseCustomException): ...


class RequestValidationException(BaseCustomException): ...


class ConflictItemsException(BaseCustomException): ...


class IdempotencyKeyException(HTTPException): ...


class NotFoundItemException(HTTPException): ...
