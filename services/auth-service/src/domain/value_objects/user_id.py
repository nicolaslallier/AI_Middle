"""User ID value object."""

import uuid
from dataclasses import dataclass

from common.domain import ValueObject


@dataclass(frozen=True)
class UserId(ValueObject):
    """User identifier value object.

    Represents a unique user identifier using UUID.
    Immutable and type-safe.

    Attributes:
        value: The UUID value
    """

    value: uuid.UUID

    @classmethod
    def generate(cls) -> "UserId":
        """Generate a new unique user ID.

        Returns:
            New UserId with random UUID
        """
        return cls(value=uuid.uuid4())

    @classmethod
    def from_string(cls, value: str) -> "UserId":
        """Create UserId from string representation.

        Args:
            value: String representation of UUID

        Returns:
            UserId instance

        Raises:
            ValueError: If string is not a valid UUID
        """
        return cls(value=uuid.UUID(value))

    def __str__(self) -> str:
        """Get string representation of user ID.

        Returns:
            String representation of UUID
        """
        return str(self.value)

