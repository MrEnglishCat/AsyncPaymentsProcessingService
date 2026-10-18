from datetime import datetime, UTC
from uuid import UUID, uuid7
from sqlalchemy import DateTime, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class UUIDMixin:

    @declared_attr
    def id(cls) -> Mapped[UUID]:
        return mapped_column(
            PG_UUID(as_uuid=True),
            primary_key=True,
            default=uuid7,
            # server_default=text("uuidv7()"), # для ее работы нужно создание в БД такой функции.
            index=True,
        )


class TimestampMixin:

    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(UTC),
            server_default=text("now()"),
            nullable=False,
        )
