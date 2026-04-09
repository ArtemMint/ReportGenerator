import logging
import os

import structlog


def setup_logging() -> None:
    """Set up structured logging with structlog, using a human-readable format in development and JSON in production."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    is_dev = os.getenv("ENV", "dev").lower() == "dev"

    # Check if we're in a development environment and use a more human-readable renderer
    renderer = structlog.dev.ConsoleRenderer() if is_dev else structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.ExceptionRenderer(),
            renderer,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__):
    """Get a structlog logger with the specified name."""
    return structlog.get_logger(name)