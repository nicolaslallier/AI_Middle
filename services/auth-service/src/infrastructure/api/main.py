"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from common.logging import configure_logging, get_logger
from src.infrastructure.api.routes import router as auth_router
from src.infrastructure.config import get_settings
from src.infrastructure.database.session import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Application lifespan manager.

    Handles startup and shutdown events.

    Args:
        app: FastAPI application

    Yields:
        None
    """
    # Startup
    settings = get_settings()

    # Configure logging
    configure_logging(
        service_name=settings.service_name,
        log_level=settings.log_level,
        json_logs=not settings.debug,
    )

    logger = get_logger()
    logger.info("Starting auth service", version="0.1.0")

    # Initialize database
    init_db(settings.database)
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down auth service")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title="Auth Service",
    description="OAuth2 Authentication and Authorization Service",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Include routers
app.include_router(auth_router)

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy", "service": "auth-service"}


@app.get("/health/ready", tags=["Health"])
async def readiness_check() -> dict[str, str]:
    """Readiness check endpoint.

    Checks if service is ready to accept requests (DB connected, etc).

    Returns:
        Readiness status
    """
    # TODO: Add database connectivity check
    return {"status": "ready", "service": "auth-service"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler.

    Args:
        request: HTTP request
        exc: Exception

    Returns:
        JSON error response
    """
    logger = get_logger()
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        path=request.url.path,
        method=request.method,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.infrastructure.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug",
    )

