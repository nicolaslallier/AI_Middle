"""Password hash value object."""

from dataclasses import dataclass

from common.domain import ValueObject


@dataclass(frozen=True)
class PasswordHash(ValueObject):
    """Password hash value object.

    Represents a hashed password (bcrypt).
    The hash itself is validated to ensure it's not empty.

    Attributes:
        value: The bcrypt hash string
    """

    value: str

    def __post_init__(self) -> None:
        """Validate hash is not empty.

        Raises:
            ValueError: If hash is empty
        """
        if not self.value or not self.value.strip():
            raise ValueError("Password hash cannot be empty")

    def __str__(self) -> str:
        """Get string representation (hash value).

        Returns:
            The hash string
        """
        return self.value

    def __repr__(self) -> str:
        """Get representation with masked hash for security.

        Returns:
            Masked representation
        """
        return "PasswordHash(***)"

