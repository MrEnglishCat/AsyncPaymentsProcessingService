import logging
import sys
from pathlib import Path


def setup_logging(level: str = "INFO", log_file: str | None = None):

    if log_file:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="[%(asctime)s] %(name)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),  # Вывод в консоль
            *([logging.FileHandler(log_file, encoding="utf-8")] if log_file else []),
        ],
    )
