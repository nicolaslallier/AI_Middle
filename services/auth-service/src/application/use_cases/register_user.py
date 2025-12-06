"""Register user use case."""

from enum import Enum

from common.result import Err, Ok, Result
from src.application.ports import IPasswordHasher, IUserRepository
from src.domain.entities import User
from src.domain.value_objects import Email


class RegistrationError(str, Enum):
    """Registration error types."""

    INVALID_EMAIL = "invalid_email"
    EMAIL_ALREADY_EXISTS = "email_already_exists"
    INVALID_PASSWORD = "invalid_password"
    REPOSITORY_ERROR = "repository_error"


class RegisterUser:
    """Use case for user registration.

    Handles the business logic for registering new users.
    Validates input, checks for existing users, hashes password,
    and persists the new user.
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher: IPasswordHasher,
    ) -> None:
        """Initialize register user use case.

        Args:
            user_repository: Repository for user persistence
            password_hasher: Service for password hashing
        """
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    async def execute(
        self,
        email: str,
        password: str,
        full_name: str,
        roles: list[str] | None = None,
    ) -> Result[User, RegistrationError]:
        """Execute user registration.

        Args:
            email: User email address
            password: Plain text password
            full_name: User's full name
            roles: Optional list of roles (defaults to ['user'])

        Returns:
            Result containing User if successful, RegistrationError otherwise
        """
        # Validate and create email value object
        email_result = Email.create(email)
        if email_result.is_err():
            return Err(RegistrationError.INVALID_EMAIL)

        email_vo = email_result.unwrap()

        # Check if user already exists
        try:
            existing_user = await self._user_repository.find_by_email(email_vo)
            if existing_user:
                return Err(RegistrationError.EMAIL_ALREADY_EXISTS)
        except Exception:
            return Err(RegistrationError.REPOSITORY_ERROR)

        # Validate password strength
        if not self._is_valid_password(password):
            return Err(RegistrationError.INVALID_PASSWORD)

        # Hash password
        try:
            password_hash = await self._password_hasher.hash(password)
        except Exception:
            return Err(RegistrationError.REPOSITORY_ERROR)

        # Create user entity
        user = User.create(
            email=email_vo,
            password_hash=password_hash,
            full_name=full_name,
            roles=roles or ["user"],
        )

        # Persist user
        try:
            await self._user_repository.save(user)
        except Exception:
            return Err(RegistrationError.REPOSITORY_ERROR)

        return Ok(user)

    @staticmethod
    def _is_valid_password(password: str) -> bool:
        """Validate password strength.

        Business rule: Password must be at least 8 characters.

        Args:
            password: Password to validate

        Returns:
            True if valid, False otherwise
        """
        if len(password) < 8:
            return False
        return True

