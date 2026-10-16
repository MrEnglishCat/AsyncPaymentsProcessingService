from typing import Type, Any
from functools import wraps
from main import main_logger


def catch_exceptions(
    exceptions: Type[Exception] | tuple[Type[Exception]],
    default_return: Any = None,
):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as error:
                main_logger.info(
                    f"Catch exception: \n\tType: {type(error)}\n\tMessage: {error.args}"
                )

                return False if default_return is None else default_return

        return wrapper

    return decorator
