import logging
import sys

from app.core.config import get_settings


def setup_logging() -> logging.Logger:
    """Configure application logging."""
    settings = get_settings()

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )

    return logging.getLogger(__name__)


logger = setup_logging()
