"""OpenTelemetry tracing configuration for distributed tracing."""

from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


def configure_tracing(service_name: str, environment: str = "development") -> None:
    """Configure OpenTelemetry tracing for the service.

    Args:
        service_name: Name of the service
        environment: Environment name (development, staging, production)

    Example:
        >>> configure_tracing("auth-service", environment="production")
        >>> tracer = get_tracer()
        >>> with tracer.start_as_current_span("user_registration"):
        ...     register_user(email="test@example.com")
    """
    # Create resource with service information
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.instance.id": f"{service_name}-1",
            "deployment.environment": environment,
        }
    )

    # Configure tracer provider
    provider = TracerProvider(resource=resource)

    # Add span processor (console exporter for development)
    # In production, replace with OTLP exporter to Jaeger/Zipkin
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)

    # Set global tracer provider
    trace.set_tracer_provider(provider)


def get_tracer(name: str = __name__) -> trace.Tracer:
    """Get a tracer instance.

    Args:
        name: Name for the tracer (usually __name__)

    Returns:
        Tracer instance

    Example:
        >>> tracer = get_tracer(__name__)
        >>> with tracer.start_as_current_span("database_query"):
        ...     result = await db.execute(query)
    """
    return trace.get_tracer(name)


def add_span_attributes(**attributes: Any) -> None:
    """Add attributes to the current span.

    Args:
        **attributes: Key-value pairs to add as span attributes

    Example:
        >>> with tracer.start_as_current_span("process_user"):
        ...     add_span_attributes(user_id=123, operation="update")
    """
    span = trace.get_current_span()
    if span:
        for key, value in attributes.items():
            span.set_attribute(key, value)


def add_span_event(name: str, **attributes: Any) -> None:
    """Add an event to the current span.

    Args:
        name: Event name
        **attributes: Key-value pairs for event attributes

    Example:
        >>> with tracer.start_as_current_span("payment_process"):
        ...     add_span_event("payment_initiated", amount=100.0, currency="USD")
    """
    span = trace.get_current_span()
    if span:
        span.add_event(name, attributes)

