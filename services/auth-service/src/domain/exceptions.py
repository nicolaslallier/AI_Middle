"""Domain exceptions for auth service."""

from common.exceptions import DomainException


class AuthDomainException(DomainException):
    """Base exception for auth domain."""

    pass


class InvalidEmailError(AuthDomainException):
    """Raised when email format is invalid."""

    def __init__(self, email: str) -> None:
        """Initialize invalid email error.

        Args:
            email: The invalid email
        """
        super().__init__(f"Invalid email format: {email}")
        self.email = email


class InvalidPasswordError(AuthDomainException):
    """Raised when password doesn't meet requirements."""

    def __init__(self, message: str) -> None:
        """Initialize invalid password error.

        Args:
            message: Description of why password is invalid
        """
        super().__init__(f"Invalid password: {message}")


class InvalidTokenError(AuthDomainException):
    """Raised when token format is invalid."""

    def __init__(self, message: str = "Invalid token format") -> None:
        """Initialize invalid token error.

        Args:
            message: Error message
        """
        super().__init__(message)


class UserAlreadyDeletedException(AuthDomainException):
    """Raised when attempting operations on deleted user."""

    def __init__(self) -> None:
        """Initialize user already deleted exception."""
        super().__init__("Cannot perform operation on deleted user")


class InvalidUserStatusTransitionError(AuthDomainException):
    """Raised when invalid status transition is attempted."""

    def __init__(self, from_status: str, to_status: str) -> None:
        """Initialize invalid status transition error.

        Args:
            from_status: Current status
            to_status: Target status
        """
        super().__init__(
            f"Invalid status transition from {from_status} to {to_status}"
        )
        self.from_status = from_status
        self.to_status = to_status

