from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from ..config.settings import settings


class BaseAlchemyModel(DeclarativeBase):

    max_print_columns: int | None = 4
    explicit_print_columns: tuple[str, ...] = tuple()

    metadata = MetaData(naming_convention=settings.db.naming_convention)

    def __repr__(self) -> str:
        columns = []
        for idx, column_name in enumerate(self.__table__.columns.keys()):
            if (
                column_name in self.explicit_print_columns
                or self.max_print_columns is None
                or idx < self.max_print_columns
            ):
                column_value = getattr(self, column_name, "<unset>")
                columns.append(f"{column_name}={column_value}")

        return f"{self.__class__.__name__}({', '.join(columns)})"

    def __str__(self) -> str:
        return self.__repr__()
