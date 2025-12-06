"""Rate limiting middleware using Redis."""

import time
from typing import Callable

import redis.asyncio as aioredis
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware.

    Uses Redis sliding window algorithm for rate limiting.
    """

    def __init__(self, app: Callable, redis_url: str, rate_limit: int = 60) -> None:
        """Initialize rate limit middleware.

        Args:
            app: ASGI application
            redis_url: Redis connection URL
            rate_limit: Number of requests allowed per minute
        """
        super().__init__(app)
        self._redis = aioredis.from_url(redis_url, decode_responses=True)
        self._rate_limit = rate_limit
        self._window_seconds = 60

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting.

        Args:
            request: HTTP request
            call_next: Next middleware

        Returns:
            HTTP response
        """
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/health/ready", "/metrics"]:
            return await call_next(request)

        # Get client identifier (IP or user ID from token)
        client_id = self._get_client_id(request)

        # Check rate limit
        is_allowed = await self._check_rate_limit(client_id)

        if not is_allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "rate_limit_exceeded",
                    "message": f"Rate limit exceeded. Max {self._rate_limit} requests per minute.",
                },
            )

        return await call_next(request)

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request.

        Args:
            request: HTTP request

        Returns:
            Client identifier
        """
        # Try to get user ID from authorization header
        auth_header = request.headers.get("authorization")
        if auth_header:
            # In production, decode JWT and get user ID
            return f"user:{auth_header[:20]}"

        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

    async def _check_rate_limit(self, client_id: str) -> bool:
        """Check if request is within rate limit.

        Args:
            client_id: Client identifier

        Returns:
            True if allowed, False if rate limit exceeded
        """
        key = f"rate_limit:{client_id}"
        current_time = int(time.time())
        window_start = current_time - self._window_seconds

        try:
            # Remove old entries
            await self._redis.zremrangebyscore(key, 0, window_start)

            # Count requests in current window
            request_count = await self._redis.zcard(key)

            if request_count >= self._rate_limit:
                return False

            # Add current request
            await self._redis.zadd(key, {str(current_time): current_time})

            # Set expiry
            await self._redis.expire(key, self._window_seconds)

            return True

        except Exception:
            # On Redis error, allow request (fail open)
            return True

