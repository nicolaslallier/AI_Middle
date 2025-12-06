"""Refresh token use case."""

from enum import Enum

from common.result import Err, Ok, Result
from src.application.ports import ITokenService, IUserRepository
from src.domain.value_objects import Token, TokenType


class RefreshTokenError(str, Enum):
    """Refresh token error types."""

    INVALID_TOKEN = "invalid_token"
    USER_NOT_FOUND = "user_not_found"
    USER_CANNOT_LOGIN = "user_cannot_login"
    REPOSITORY_ERROR = "repository_error"


class RefreshToken:
    """Use case for refreshing access tokens.

    Handles the business logic for refreshing access tokens
    using refresh tokens.
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        token_service: ITokenService,
    ) -> None:
        """Initialize refresh token use case.

        Args:
            user_repository: Repository for user persistence
            token_service: Service for token operations
        """
        self._user_repository = user_repository
        self._token_service = token_service

    async def execute(
        self,
        refresh_token_string: str,
    ) -> Result[Token, RefreshTokenError]:
        """Execute token refresh.

        Args:
            refresh_token_string: Refresh token string

        Returns:
            Result containing new access Token if successful, error otherwise
        """
        # Create refresh token value object
        try:
            refresh_token = Token(
                value=refresh_token_string,
                type=TokenType.REFRESH,
                expires_at=None,  # Will be validated by service
            )
        except Exception:
            return Err(RefreshTokenError.INVALID_TOKEN)

        # Verify refresh token and get user ID
        try:
            user_id = await self._token_service.verify_token(refresh_token)
            if not user_id:
                return Err(RefreshTokenError.INVALID_TOKEN)
        except Exception:
            return Err(RefreshTokenError.INVALID_TOKEN)

        # Find user
        try:
            user = await self._user_repository.find_by_id(user_id)
            if not user:
                return Err(RefreshTokenError.USER_NOT_FOUND)
        except Exception:
            return Err(RefreshTokenError.REPOSITORY_ERROR)

        # Check if user can login (business rule)
        if not user.can_login():
            return Err(RefreshTokenError.USER_CANNOT_LOGIN)

        # Generate new access token
        try:
            new_access_token = await self._token_service.generate_access_token(
                user.id, user.roles
            )
        except Exception:
            return Err(RefreshTokenError.REPOSITORY_ERROR)

        return Ok(new_access_token)

