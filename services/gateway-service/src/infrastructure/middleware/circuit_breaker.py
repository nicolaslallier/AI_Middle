"""Circuit breaker implementation."""

import time
from enum import Enum
from typing import Any, Callable


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker for external service calls.

    Prevents cascading failures by failing fast when service is down.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type[Exception] = Exception,
    ) -> None:
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before trying half-open
            expected_exception: Exception type to catch
        """
        self._failure_threshold = failure_threshold
        self._timeout = timeout
        self._expected_exception = expected_exception
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._state = CircuitState.CLOSED

    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Call function with circuit breaker protection.

        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If circuit is open or function raises
        """
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time >= self._timeout:
                self._state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)

            # Success - reset on half-open or stay closed
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.CLOSED
                self._failure_count = 0

            return result

        except self._expected_exception as e:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._failure_count >= self._failure_threshold:
                self._state = CircuitState.OPEN

            raise

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state

