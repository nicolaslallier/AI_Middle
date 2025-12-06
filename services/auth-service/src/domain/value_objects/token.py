"""Token value object."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from common.domain import ValueObject
from src.domain.exceptions import InvalidTokenError


class TokenType(str, Enum):
    """Type of authentication token."""

    ACCESS = "access"
    REFRESH = "refresh"


@dataclass(frozen=True)
class Token(ValueObject):
    """Authentication token value object.

    Represents a JWT token with its type and expiration.
    Immutable and validates token structure.

    Attributes:
        value: The token string (JWT)
        type: Type of token (access or refresh)
        expires_at: When the token expires
    """

    value: str
    type: TokenType
    expires_at: datetime

    def __post_init__(self) -> None:
        """Validate token is not empty.

        Raises:
            InvalidTokenError: If token is empty
        """
        if not self.value or not self.value.strip():
            raise InvalidTokenError("Token cannot be empty")

    def is_expired(self) -> bool:
        """Check if token has expired.

        Returns:
            True if token is expired, False otherwise
        """
        from datetime import timezone

        return datetime.now(timezone.utc) > self.expires_at

    def __str__(self) -> str:
        """Get string representation of token.

        Returns:
            Token value
        """
        return self.value

    def __repr__(self) -> str:
        """Get representation with masked token for security.

        Returns:
            Masked representation
        """
        return f"Token(type={self.type}, expires_at={self.expires_at}, ***)"

