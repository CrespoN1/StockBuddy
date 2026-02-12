"""
Structured logging configuration using structlog.

- Development: colored, human-readable console output
- Production: JSON lines for Railway / log aggregation
"""

import logging
import sys

import structlog

from app.config import settings


def setup_logging() -> None:
    """Configure structlog for the application."""
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.environment == "production":
        # JSON for Railway / log aggregation
        shared_processors.append(structlog.processors.format_exc_info)
        shared_processors.append(structlog.processors.JSONRenderer())
    else:
        # Pretty console for development
        shared_processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=shared_processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Set root log level from settings
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
    )
