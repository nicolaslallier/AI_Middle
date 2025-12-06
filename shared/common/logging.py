"""Structured logging configuration for all services."""

import logging
import sys
from typing import Any

import structlog
from structlog.typing import EventDict, Processor


def add_log_level(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add log level to event dictionary.

    Args:
        logger: Logger instance
        method_name: Name of the logging method
        event_dict: Event dictionary to modify

    Returns:
        Modified event dictionary with log level
    """
    event_dict["level"] = method_name.upper()
    return event_dict


def add_timestamp(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add ISO timestamp to event dictionary.

    Args:
        logger: Logger instance
        method_name: Name of the logging method
        event_dict: Event dictionary to modify

    Returns:
        Modified event dictionary with timestamp
    """
    import datetime

    event_dict["timestamp"] = datetime.datetime.utcnow().isoformat()
    return event_dict


def configure_logging(
    service_name: str,
    log_level: str = "INFO",
    json_logs: bool = True,
) -> None:
    """Configure structured logging for the service.

    Args:
        service_name: Name of the service (added to all logs)
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: If True, output JSON logs. If False, use console format.

    Example:
        >>> configure_logging("auth-service", log_level="DEBUG")
        >>> logger = structlog.get_logger()
        >>> logger.info("user_registered", user_id=123, email="test@example.com")
    """
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Build processor chain
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        add_log_level,
        add_timestamp,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Add JSON or console renderer
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Add service name to all logs
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(service=service_name)


def get_logger() -> structlog.stdlib.BoundLogger:
    """Get a configured logger instance.

    Returns:
        Configured logger instance

    Example:
        >>> logger = get_logger()
        >>> logger.info("operation_completed", duration_ms=150)
    """
    return structlog.get_logger()

