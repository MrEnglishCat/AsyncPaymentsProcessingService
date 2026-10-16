from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from .mixins import UUIDMixin, TimestampMixin
from ..models.base import BaseAlchemyModel
from ..enums import OutboxStatus


class Outbox(
    BaseAlchemyModel,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "outboxes"

    event_type: Mapped[str] = mapped_column(String(50))
    payload: Mapped[dict] = mapped_column(JSONB, default={})
    status: Mapped[OutboxStatus] = mapped_column(
        String(30),
        default=OutboxStatus.PENDING,
        index=True,
    )
    attempts: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
