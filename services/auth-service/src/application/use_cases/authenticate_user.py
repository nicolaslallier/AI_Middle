"""Authenticate user use case."""

from dataclasses import dataclass
from enum import Enum

from common.result import Err, Ok, Result
from src.application.ports import IPasswordHasher, ITokenService, IUserRepository
from src.domain.value_objects import Email, Token


class AuthenticationError(str, Enum):
    """Authentication error types."""

    INVALID_EMAIL = "invalid_email"
    INVALID_CREDENTIALS = "invalid_credentials"
    USER_NOT_FOUND = "user_not_found"
    USER_CANNOT_LOGIN = "user_cannot_login"
    REPOSITORY_ERROR = "repository_error"


@dataclass
class AuthenticationResult:
    """Result of successful authentication."""

    access_token: Token
    refresh_token: Token
    user_id: str
    email: str
    roles: list[str]


class AuthenticateUser:
    """Use case for user authentication.

    Handles the business logic for authenticating users.
    Validates credentials, checks user status, generates tokens.
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher: IPasswordHasher,
        token_service: ITokenService,
    ) -> None:
        """Initialize authenticate user use case.

        Args:
            user_repository: Repository for user persistence
            password_hasher: Service for password hashing
            token_service: Service for token generation
        """
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_service = token_service

    async def execute(
        self,
        email: str,
        password: str,
    ) -> Result[AuthenticationResult, AuthenticationError]:
        """Execute user authentication.

        Args:
            email: User email address
            password: Plain text password

        Returns:
            Result containing AuthenticationResult if successful, error otherwise
        """
        # Validate and create email value object
        email_result = Email.create(email)
        if email_result.is_err():
            return Err(AuthenticationError.INVALID_EMAIL)

        email_vo = email_result.unwrap()

        # Find user by email
        try:
            user = await self._user_repository.find_by_email(email_vo)
            if not user:
                return Err(AuthenticationError.USER_NOT_FOUND)
        except Exception:
            return Err(AuthenticationError.REPOSITORY_ERROR)

        # Verify password
        try:
            is_valid = await self._password_hasher.verify(password, user.password_hash)
            if not is_valid:
                return Err(AuthenticationError.INVALID_CREDENTIALS)
        except Exception:
            return Err(AuthenticationError.REPOSITORY_ERROR)

        # Check if user can login (business rule)
        if not user.can_login():
            return Err(AuthenticationError.USER_CANNOT_LOGIN)

        # Update last login
        user.mark_login()
        try:
            await self._user_repository.save(user)
        except Exception:
            # Non-critical - continue with authentication
            pass

        # Generate tokens
        try:
            access_token = await self._token_service.generate_access_token(
                user.id, user.roles
            )
            refresh_token = await self._token_service.generate_refresh_token(user.id)
        except Exception:
            return Err(AuthenticationError.REPOSITORY_ERROR)

        return Ok(
            AuthenticationResult(
                access_token=access_token,
                refresh_token=refresh_token,
                user_id=str(user.id),
                email=str(user.email),
                roles=user.roles,
            )
        )

