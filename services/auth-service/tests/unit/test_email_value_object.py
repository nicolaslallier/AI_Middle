"""Unit tests for Email value object."""

import pytest

from src.domain.exceptions import InvalidEmailError
from src.domain.value_objects import Email


class TestEmail:
    """Test cases for Email value object."""

    def test_create_valid_email_succeeds(self) -> None:
        """GIVEN valid email string
        WHEN creating Email
        THEN Email is created successfully
        """
        # Arrange
        email_str = "test@example.com"

        # Act
        result = Email.create(email_str)

        # Assert
        assert result.is_ok()
        email = result.unwrap()
        assert str(email) == "test@example.com"

    def test_create_email_normalizes_case(self) -> None:
        """GIVEN email with mixed case
        WHEN creating Email
        THEN email is normalized to lowercase
        """
        # Arrange & Act
        result = Email.create("Test@EXAMPLE.COM")

        # Assert
        assert result.is_ok()
        assert str(result.unwrap()) == "test@example.com"

    def test_create_email_strips_whitespace(self) -> None:
        """GIVEN email with whitespace
        WHEN creating Email
        THEN whitespace is stripped
        """
        # Arrange & Act
        result = Email.create("  test@example.com  ")

        # Assert
        assert result.is_ok()
        assert str(result.unwrap()) == "test@example.com"

    def test_create_invalid_email_fails(self) -> None:
        """GIVEN invalid email string
        WHEN creating Email
        THEN creation fails with error
        """
        # Arrange & Act
        result = Email.create("not-an-email")

        # Assert
        assert result.is_err()

    def test_create_empty_email_fails(self) -> None:
        """GIVEN empty email string
        WHEN creating Email
        THEN creation fails with error
        """
        # Arrange & Act
        result = Email.create("")

        # Assert
        assert result.is_err()

    def test_emails_with_same_value_are_equal(self) -> None:
        """GIVEN two emails with same value
        WHEN comparing them
        THEN they are equal
        """
        # Arrange & Act
        email1 = Email.create("test@example.com").unwrap()
        email2 = Email.create("test@example.com").unwrap()

        # Assert
        assert email1 == email2

    def test_email_is_immutable(self) -> None:
        """GIVEN an email
        WHEN trying to modify it
        THEN it raises error (frozen dataclass)
        """
        # Arrange
        email = Email.create("test@example.com").unwrap()

        # Act & Assert
        with pytest.raises(Exception):
            email.value = "different@example.com"  # type: ignore

