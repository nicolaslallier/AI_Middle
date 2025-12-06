"""Token service port (interface)."""

from abc import ABC, abstractmethod

from src.domain.value_objects import Token, TokenType, UserId


class ITokenService(ABC):
    """Port for token generation and validation.

    Defines the contract for JWT token operations.
    Implementations are in the infrastructure layer.
    """

    @abstractmethod
    async def generate_access_token(self, user_id: UserId, roles: list[str]) -> Token:
        """Generate access token for user.

        Args:
            user_id: User identifier
            roles: User roles to include in token

        Returns:
            Access token
        """
        pass

    @abstractmethod
    async def generate_refresh_token(self, user_id: UserId) -> Token:
        """Generate refresh token for user.

        Args:
            user_id: User identifier

        Returns:
            Refresh token
        """
        pass

    @abstractmethod
    async def verify_token(self, token: Token) -> UserId | None:
        """Verify and decode token.

        Args:
            token: Token to verify

        Returns:
            User ID if valid, None otherwise
        """
        pass

    @abstractmethod
    async def refresh_access_token(self, refresh_token: Token) -> Token | None:
        """Generate new access token from refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            New access token if refresh token is valid, None otherwise
        """
        pass

