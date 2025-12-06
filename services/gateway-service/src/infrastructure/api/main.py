"""FastAPI application for gateway service."""

from contextlib import asynccontextmanager
from typing import Any

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from common.logging import configure_logging, get_logger
from src.infrastructure.config import get_settings
from src.infrastructure.middleware.circuit_breaker import CircuitBreaker
from src.infrastructure.middleware.rate_limiter import RateLimitMiddleware

# Circuit breakers for backend services
auth_circuit = CircuitBreaker(failure_threshold=5, timeout=60)
aggregation_circuit = CircuitBreaker(failure_threshold=5, timeout=60)


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Application lifespan manager."""
    settings = get_settings()

    # Configure logging
    configure_logging(
        service_name=settings.service_name,
        log_level=settings.log_level,
    )

    logger = get_logger()
    logger.info("Starting gateway service")

    yield

    logger.info("Shutting down gateway service")


app = FastAPI(
    title="Gateway Service",
    description="API Gateway with Rate Limiting and Circuit Breaker",
    version="0.1.0",
    lifespan=lifespan,
)

# Add rate limiting middleware
settings = get_settings()
app.add_middleware(
    RateLimitMiddleware,
    redis_url=settings.redis.url,
    rate_limit=settings.rate_limit_per_minute,
)

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "gateway-service"}


@app.get("/health/ready")
async def readiness_check() -> dict[str, str]:
    """Readiness check endpoint."""
    return {"status": "ready", "service": "gateway-service"}


@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_auth(request: Request, path: str) -> JSONResponse:
    """Proxy requests to auth service.

    Args:
        request: HTTP request
        path: Request path

    Returns:
        Response from auth service
    """
    settings = get_settings()
    url = f"{settings.auth_service_url}/{path}"

    async def make_request() -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=url,
                headers=dict(request.headers),
                content=await request.body(),
            )
            return response

    try:
        response = await auth_circuit.call(make_request)
        return JSONResponse(
            content=response.json() if response.content else {},
            status_code=response.status_code,
        )
    except Exception as e:
        return JSONResponse(
            content={"error": "service_unavailable", "message": str(e)},
            status_code=503,
        )


@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_aggregation(request: Request, path: str) -> JSONResponse:
    """Proxy requests to aggregation service.

    Args:
        request: HTTP request
        path: Request path

    Returns:
        Response from aggregation service
    """
    settings = get_settings()
    url = f"{settings.aggregation_service_url}/{path}"

    async def make_request() -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=url,
                headers=dict(request.headers),
                content=await request.body(),
            )
            return response

    try:
        response = await aggregation_circuit.call(make_request)
        return JSONResponse(
            content=response.json() if response.content else {},
            status_code=response.status_code,
        )
    except Exception as e:
        return JSONResponse(
            content={"error": "service_unavailable", "message": str(e)},
            status_code=503,
        )

