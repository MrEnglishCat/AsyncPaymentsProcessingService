from typing import Annotated

from fastapi import Header


def get_header_dependency(
    header_name: str, default_value: str = "", description: str = ""
):
    def dependency(
        header: Annotated[
            str,
            Header(
                alias=header_name,
                description=description,
            ),
        ] = default_value,
    ) -> str:
        return header

    return dependency
