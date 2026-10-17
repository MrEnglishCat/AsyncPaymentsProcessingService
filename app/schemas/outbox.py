from pydantic import BaseModel, Field
from ..enums import OutboxStatusEnum
from .base import IDSchema


class OutboxSchema(BaseModel):
    event_type: str = Field(max_length=50)
    payload: dict = Field(default_factory=dict)
    status: OutboxStatusEnum = Field(default=OutboxStatusEnum.PENDING, max_length=30)
    attemts: int = Field(default=0)
    error_message: str | None = Field(max_length=1000)


# DEVELOPMENT ???
class OutboxCreateSchema(OutboxSchema): ...


class OutboxReadSchema(IDSchema, OutboxSchema): ...
