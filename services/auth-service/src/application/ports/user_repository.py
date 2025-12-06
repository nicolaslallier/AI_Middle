"""User repository port (interface)."""

from abc import ABC, abstractmethod

from src.domain.entities import User
from src.domain.value_objects import Email, UserId


class IUserRepository(ABC):
    """Port for user repository.

    Defines the contract for user persistence operations.
    Implementations are in the adapters layer.
    """

    @abstractmethod
    async def find_by_id(self, user_id: UserId) -> User | None:
        """Find user by ID.

        Args:
            user_id: User identifier

        Returns:
            User if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_email(self, email: Email) -> User | None:
        """Find user by email.

        Args:
            email: User email

        Returns:
            User if found, None otherwise
        """
        pass

    @abstractmethod
    async def save(self, user: User) -> None:
        """Save user (create or update).

        Args:
            user: User entity to save
        """
        pass

    @abstractmethod
    async def delete(self, user_id: UserId) -> None:
        """Delete user by ID.

        Args:
            user_id: User identifier
        """
        pass

    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        """Check if user exists by email.

        Args:
            email: User email

        Returns:
            True if user exists, False otherwise
        """
        pass

