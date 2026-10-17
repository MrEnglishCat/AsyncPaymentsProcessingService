from enum import StrEnum
from typing import Any, TypeVar, Generic

from pydantic import Field, BaseModel


class ResponseStatus(StrEnum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    model_config = {"from_attributes": True}

    status: ResponseStatus
    message: str
    data: T | None = None
    warnings: list[str] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)


class ResponseOk(BaseResponse[T]):
    status: ResponseStatus = ResponseStatus.OK
    message: str = "Operation completed successfully"


class ResponseWarning(BaseResponse[T]):
    status: ResponseStatus = ResponseStatus.WARNING
    message: str = "Operation completed with warnings"
    warnings: list[str] = Field(default_factory=list)


class ResponseError(BaseResponse[T]):
    status: ResponseStatus = ResponseStatus.ERROR
    message: str = "Operation failed"
    errors: list[dict[str, Any]] = Field(default_factory=list)


class ResponseFactory:

    @staticmethod
    def ok(
        data: T | None = None,
        message: str = "Success",
        as_dict: bool = False,
        mode: str = "python",
    ) -> ResponseOk:
        response = ResponseOk(data=data, message=message)
        return response.model_dump(mode=mode) if as_dict else response

    @staticmethod
    def warning(
        data: T | None = None,
        message: str = "Operation completed with warnings",
        warnings: list[str] | None = None,
        as_dict: bool = False,
        mode: str = "python",
    ) -> ResponseWarning:
        response = ResponseWarning(message=message, data=data, warnings=warnings or [])
        return response.model_dump(mode=mode) if as_dict else response

    @staticmethod
    def error(
        data: T | None = None,
        message: str = "Operation failed",
        errors: list[dict[str, Any]] | None = None,
        as_dict: bool = False,
        mode: str = "python",
    ):
        response = ResponseError(data=data, message=message, errors=errors or [])
        return response.model_dump(mode=mode) if as_dict else response
