"""JWT token service implementation."""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from src.application.ports import ITokenService
from src.domain.value_objects import Token, TokenType, UserId
from src.infrastructure.config import JWTSettings


class JWTTokenService(ITokenService):
    """JWT implementation of token service.

    Uses python-jose for JWT token generation and verification.
    """

    def __init__(self, settings: JWTSettings) -> None:
        """Initialize JWT token service.

        Args:
            settings: JWT configuration settings
        """
        self._secret_key = settings.secret_key
        self._algorithm = settings.algorithm
        self._access_token_expire_minutes = settings.access_token_expire_minutes
        self._refresh_token_expire_days = settings.refresh_token_expire_days

    async def generate_access_token(self, user_id: UserId, roles: list[str]) -> Token:
        """Generate access token for user.

        Args:
            user_id: User identifier
            roles: User roles to include in token

        Returns:
            Access token
        """
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self._access_token_expire_minutes
        )

        payload = {
            "sub": str(user_id),
            "type": TokenType.ACCESS.value,
            "roles": roles,
            "exp": expires_at,
            "iat": datetime.now(timezone.utc),
        }

        token_value = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

        return Token(
            value=token_value,
            type=TokenType.ACCESS,
            expires_at=expires_at,
        )

    async def generate_refresh_token(self, user_id: UserId) -> Token:
        """Generate refresh token for user.

        Args:
            user_id: User identifier

        Returns:
            Refresh token
        """
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=self._refresh_token_expire_days
        )

        payload = {
            "sub": str(user_id),
            "type": TokenType.REFRESH.value,
            "exp": expires_at,
            "iat": datetime.now(timezone.utc),
        }

        token_value = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

        return Token(
            value=token_value,
            type=TokenType.REFRESH,
            expires_at=expires_at,
        )

    async def verify_token(self, token: Token) -> UserId | None:
        """Verify and decode token.

        Args:
            token: Token to verify

        Returns:
            User ID if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                str(token),
                self._secret_key,
                algorithms=[self._algorithm],
            )

            user_id_str: str | None = payload.get("sub")
            if not user_id_str:
                return None

            return UserId.from_string(user_id_str)

        except JWTError:
            return None

    async def refresh_access_token(self, refresh_token: Token) -> Token | None:
        """Generate new access token from refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            New access token if refresh token is valid, None otherwise
        """
        try:
            payload = jwt.decode(
                str(refresh_token),
                self._secret_key,
                algorithms=[self._algorithm],
            )

            # Verify token type
            token_type = payload.get("type")
            if token_type != TokenType.REFRESH.value:
                return None

            user_id_str: str | None = payload.get("sub")
            if not user_id_str:
                return None

            user_id = UserId.from_string(user_id_str)

            # Generate new access token
            # Note: roles would need to be fetched from database
            return await self.generate_access_token(user_id, [])

        except JWTError:
            return None

