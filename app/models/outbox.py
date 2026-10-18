from datetime import datetime

from sqlalchemy import DateTime, Index, String, Enum as SA_Enum, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from .mixins import UUIDMixin, TimestampMixin
from ..models.base import BaseAlchemyModel
from ..enums import OutboxStatusEnum


class Outbox(
    BaseAlchemyModel,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "outboxes"

    event_type: Mapped[str] = mapped_column(String(50))
    payload: Mapped[dict] = mapped_column(JSONB, default={})
    status: Mapped[OutboxStatusEnum] = mapped_column(
        SA_Enum(
            OutboxStatusEnum,
            name="status",
            create_type=False,
            native_enum=False,
            length=255,
        ),
        index=True,
        default=OutboxStatusEnum.PENDING,
    )
    attempts: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index(
            "ix_outbox_pending_created",
            "created_at",
            postgresql_where=text(f"status = '{OutboxStatusEnum.PENDING}'"),
        ),
        Index(
            "ix_outbox_locked_until",
            "locked_until",
            postgresql_where=text(f"status = '{OutboxStatusEnum.PROCESSING}'"),
        ),
    )
