"""FastAPI application for aggregation service."""

from contextlib import asynccontextmanager
from typing import Any

import redis.asyncio as aioredis
from fastapi import FastAPI
from prometheus_client import make_asgi_app

from common.logging import configure_logging, get_logger
from src.infrastructure.config import get_settings

# Global Redis client
redis_client: aioredis.Redis | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Application lifespan manager."""
    global redis_client

    settings = get_settings()

    # Configure logging
    configure_logging(
        service_name=settings.service_name,
        log_level=settings.log_level,
    )

    logger = get_logger()
    logger.info("Starting aggregation service")

    # Initialize Redis
    redis_client = aioredis.from_url(settings.redis.url, decode_responses=True)
    logger.info("Redis initialized")

    yield

    logger.info("Shutting down aggregation service")
    if redis_client:
        await redis_client.close()


app = FastAPI(
    title="Aggregation Service",
    description="Data Aggregation and Transformation Service",
    version="0.1.0",
    lifespan=lifespan,
)

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "aggregation-service"}


@app.get("/health/ready")
async def readiness_check() -> dict[str, str]:
    """Readiness check endpoint."""
    return {"status": "ready", "service": "aggregation-service"}


@app.get("/data/aggregate")
async def aggregate_data(sources: str = "all") -> dict[str, Any]:
    """Aggregate data from multiple sources.

    Args:
        sources: Comma-separated list of sources or 'all'

    Returns:
        Aggregated data
    """
    logger = get_logger()
    logger.info("Aggregating data", sources=sources)

    # This is a placeholder - in production would fetch from multiple backends
    return {
        "status": "success",
        "sources": sources.split(","),
        "data": {
            "example": "Aggregated data would go here",
            "timestamp": "2024-01-01T00:00:00Z",
        },
    }


@app.post("/data/transform")
async def transform_data(data: dict[str, Any]) -> dict[str, Any]:
    """Transform data according to business rules.

    Args:
        data: Data to transform

    Returns:
        Transformed data
    """
    logger = get_logger()
    logger.info("Transforming data")

    # This is a placeholder - in production would apply transformations
    return {
        "status": "success",
        "original": data,
        "transformed": {
            **data,
            "processed": True,
            "timestamp": "2024-01-01T00:00:00Z",
        },
    }

