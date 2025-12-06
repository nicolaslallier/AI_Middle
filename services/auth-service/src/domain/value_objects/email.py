"""Email value object."""

import re
from dataclasses import dataclass

from common.domain import ValueObject
from common.result import Err, Ok, Result
from src.domain.exceptions import InvalidEmailError


@dataclass(frozen=True)
class Email(ValueObject):
    """Email address value object.

    Represents a validated email address.
    Immutable and guarantees email format validity.

    Attributes:
        value: The email address string
    """

    value: str

    def __post_init__(self) -> None:
        """Validate email format after initialization.

        Raises:
            InvalidEmailError: If email format is invalid
        """
        if not self._is_valid_format(self.value):
            raise InvalidEmailError(self.value)

    @classmethod
    def create(cls, value: str) -> Result["Email", str]:
        """Create Email with validation, returning Result.

        Args:
            value: Email string to validate

        Returns:
            Result containing Email if valid, error message if invalid
        """
        if not value:
            return Err("Email cannot be empty")

        normalized = value.lower().strip()

        if not cls._is_valid_format(normalized):
            return Err(f"Invalid email format: {value}")

        try:
            return Ok(cls(value=normalized))
        except InvalidEmailError as e:
            return Err(str(e))

    @staticmethod
    def _is_valid_format(email: str) -> bool:
        """Validate email format using regex.

        Args:
            email: Email string to validate

        Returns:
            True if valid format, False otherwise
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def __str__(self) -> str:
        """Get string representation of email.

        Returns:
            Email address as string
        """
        return self.value

