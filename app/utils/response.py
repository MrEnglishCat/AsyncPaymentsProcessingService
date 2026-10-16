from enum import StrEnum
from typing import Any

from pydantic import Field, BaseModel


class ResponseStatus(StrEnum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


class BaseResponse(BaseModel):
    status: ResponseStatus
    message: str
    data: Any | None = None
    warnings: list[str] = None
    errors: list[dict[str, Any]] | None = None


class ResponseOk(BaseResponse):
    status: ResponseStatus = ResponseStatus.OK
    message: str = "Operation completed successfully"


class ResponseWarning(BaseResponse):
    status: ResponseStatus = ResponseStatus.WARNING
    message: str = "Operation completed with warnings"
    warnings: list[str] = Field(default_factory=list)


class ResponseError(BaseResponse):
    status: ResponseStatus = ResponseStatus.ERROR
    message: str = "Operation failed"
    errors: list[dict[str, Any]] | None = Field(default_factory=list)


class ResponseFactory:

    @staticmethod
    def ok(data: Any = None, message: str = "Success") -> ResponseOk:
        return ResponseOk(data=data, message=message)

    @staticmethod
    def warning(
        data: Any = None,
        message: str = "Operation completed with warnings",
        warnings: list[str] | None = None,
    ) -> ResponseWarning:
        return ResponseWarning(message=message, data=data, warnings=warnings or [])

    @staticmethod
    def error(
        data: Any = None,
        message: str = "Operation failed",
        errors: list[dict[str, Any]] | None = None,
    ):
        return ResponseError(data=data, message=message, errors=errors)
