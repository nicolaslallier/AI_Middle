"""Password hasher port (interface)."""

from abc import ABC, abstractmethod

from src.domain.value_objects import PasswordHash


class IPasswordHasher(ABC):
    """Port for password hashing operations.

    Defines the contract for password hashing and verification.
    Implementations are in the infrastructure layer.
    """

    @abstractmethod
    async def hash(self, plain_password: str) -> PasswordHash:
        """Hash a plain text password.

        Args:
            plain_password: Plain text password to hash

        Returns:
            PasswordHash containing the bcrypt hash
        """
        pass

    @abstractmethod
    async def verify(self, plain_password: str, password_hash: PasswordHash) -> bool:
        """Verify a password against a hash.

        Args:
            plain_password: Plain text password to verify
            password_hash: Hash to verify against

        Returns:
            True if password matches hash, False otherwise
        """
        pass

