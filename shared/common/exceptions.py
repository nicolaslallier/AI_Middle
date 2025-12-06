"""Common exception hierarchy for all services."""

from typing import Any


class BaseException(Exception):
    """Base exception for all custom exceptions."""

    def __init__(self, message: str, *args: Any) -> None:
        """Initialize base exception.

        Args:
            message: Human-readable error message
            *args: Additional arguments
        """
        self.message = message
        super().__init__(message, *args)


class DomainException(BaseException):
    """Base exception for domain-level errors.

    Domain exceptions represent business rule violations.
    They should be raised when domain invariants are violated.
    """

    pass


class ApplicationException(BaseException):
    """Base exception for application-level errors.

    Application exceptions represent use case failures.
    They should be raised when a use case cannot be completed.
    """

    pass


class InfrastructureException(BaseException):
    """Base exception for infrastructure-level errors.

    Infrastructure exceptions represent failures in external systems
    like databases, message queues, or third-party APIs.
    """

    pass


class ValidationException(DomainException):
    """Exception raised when validation fails."""

    def __init__(self, field: str, message: str) -> None:
        """Initialize validation exception.

        Args:
            field: Field name that failed validation
            message: Validation error message
        """
        self.field = field
        super().__init__(f"Validation error for '{field}': {message}")


class NotFoundException(ApplicationException):
    """Exception raised when a resource is not found."""

    def __init__(self, resource_type: str, identifier: str) -> None:
        """Initialize not found exception.

        Args:
            resource_type: Type of resource (e.g., "User", "Order")
            identifier: Identifier used in search
        """
        self.resource_type = resource_type
        self.identifier = identifier
        super().__init__(f"{resource_type} not found: {identifier}")


class AlreadyExistsException(ApplicationException):
    """Exception raised when attempting to create a resource that already exists."""

    def __init__(self, resource_type: str, identifier: str) -> None:
        """Initialize already exists exception.

        Args:
            resource_type: Type of resource (e.g., "User", "Order")
            identifier: Identifier that already exists
        """
        self.resource_type = resource_type
        self.identifier = identifier
        super().__init__(f"{resource_type} already exists: {identifier}")


class UnauthorizedException(ApplicationException):
    """Exception raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed") -> None:
        """Initialize unauthorized exception.

        Args:
            message: Error message
        """
        super().__init__(message)


class ForbiddenException(ApplicationException):
    """Exception raised when authorization fails."""

    def __init__(self, message: str = "Access forbidden") -> None:
        """Initialize forbidden exception.

        Args:
            message: Error message
        """
        super().__init__(message)


class DatabaseException(InfrastructureException):
    """Exception raised when database operations fail."""

    pass


class ExternalServiceException(InfrastructureException):
    """Exception raised when external service calls fail."""

    def __init__(self, service_name: str, message: str) -> None:
        """Initialize external service exception.

        Args:
            service_name: Name of the external service
            message: Error message
        """
        self.service_name = service_name
        super().__init__(f"External service '{service_name}' error: {message}")

