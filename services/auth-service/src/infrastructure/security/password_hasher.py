"""Password hasher implementation using bcrypt."""

from passlib.context import CryptContext

from src.application.ports import IPasswordHasher
from src.domain.value_objects import PasswordHash

# Configure password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BcryptPasswordHasher(IPasswordHasher):
    """Bcrypt implementation of password hasher.

    Uses passlib with bcrypt for secure password hashing.
    """

    async def hash(self, plain_password: str) -> PasswordHash:
        """Hash a plain text password.

        Args:
            plain_password: Plain text password to hash

        Returns:
            PasswordHash containing the bcrypt hash
        """
        hash_str = pwd_context.hash(plain_password)
        return PasswordHash(value=hash_str)

    async def verify(self, plain_password: str, password_hash: PasswordHash) -> bool:
        """Verify a password against a hash.

        Args:
            plain_password: Plain text password to verify
            password_hash: Hash to verify against

        Returns:
            True if password matches hash, False otherwise
        """
        return pwd_context.verify(plain_password, str(password_hash))

