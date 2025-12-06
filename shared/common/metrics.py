"""Prometheus metrics utilities for all services."""

import functools
import time
from typing import Any, Callable, TypeVar, cast

from prometheus_client import Counter, Histogram, Summary

# Type variable for decorated functions
F = TypeVar("F", bound=Callable[..., Any])


# Define common metrics
request_count = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

database_query_duration = Histogram(
    "database_query_duration_seconds",
    "Database query duration in seconds",
    ["operation"],
)

cache_operations = Counter(
    "cache_operations_total",
    "Total cache operations",
    ["operation", "result"],
)

external_api_calls = Counter(
    "external_api_calls_total",
    "Total external API calls",
    ["service", "status"],
)

business_operations = Counter(
    "business_operations_total",
    "Total business operations",
    ["operation", "result"],
)


def track_time(metric: Histogram | Summary, labels: dict[str, str] | None = None) -> Callable[[F], F]:
    """Decorator to track execution time of a function.

    Args:
        metric: Prometheus Histogram or Summary metric
        labels: Optional labels to add to the metric

    Returns:
        Decorated function

    Example:
        >>> @track_time(database_query_duration, {"operation": "find_user"})
        >>> async def find_user(user_id: int) -> User:
        ...     return await db.query(User).filter(User.id == user_id).first()
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                if labels:
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                if labels:
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        return cast(F, sync_wrapper)

    return decorator


def count_calls(
    counter: Counter,
    labels: dict[str, str] | None = None,
) -> Callable[[F], F]:
    """Decorator to count function calls.

    Args:
        counter: Prometheus Counter metric
        labels: Optional labels to add to the metric

    Returns:
        Decorated function

    Example:
        >>> @count_calls(business_operations, {"operation": "user_registration"})
        >>> async def register_user(email: str) -> User:
        ...     return await create_user(email)
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                result = await func(*args, **kwargs)
                if labels:
                    counter.labels(**labels, result="success").inc()
                else:
                    counter.labels(result="success").inc()
                return result
            except Exception as e:
                if labels:
                    counter.labels(**labels, result="error").inc()
                else:
                    counter.labels(result="error").inc()
                raise

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                result = func(*args, **kwargs)
                if labels:
                    counter.labels(**labels, result="success").inc()
                else:
                    counter.labels(result="success").inc()
                return result
            except Exception as e:
                if labels:
                    counter.labels(**labels, result="error").inc()
                else:
                    counter.labels(result="error").inc()
                raise

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        return cast(F, sync_wrapper)

    return decorator

