"""Authentication controller."""

from fastapi import HTTPException, status

from src.adapters.dtos import (
    AuthenticationRequest,
    AuthenticationResponse,
    ErrorResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterUserRequest,
    UserResponse,
)
from src.application.use_cases import AuthenticateUser, RefreshToken, RegisterUser
from src.application.use_cases.authenticate_user import AuthenticationError
from src.application.use_cases.refresh_token import RefreshTokenError
from src.application.use_cases.register_user import RegistrationError


class AuthController:
    """Controller for authentication endpoints.

    Thin controller that delegates to use cases and maps results to HTTP responses.
    Contains no business logic - only request/response handling.
    """

    def __init__(
        self,
        register_user: RegisterUser,
        authenticate_user: AuthenticateUser,
        refresh_token: RefreshToken,
    ) -> None:
        """Initialize auth controller.

        Args:
            register_user: Register user use case
            authenticate_user: Authenticate user use case
            refresh_token: Refresh token use case
        """
        self._register_user = register_user
        self._authenticate_user = authenticate_user
        self._refresh_token = refresh_token

    async def register(self, request: RegisterUserRequest) -> UserResponse:
        """Handle user registration request.

        Args:
            request: Registration request

        Returns:
            User response

        Raises:
            HTTPException: If registration fails
        """
        result = await self._register_user.execute(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            roles=request.roles,
        )

        if result.is_err():
            error = result.unwrap_err()
            raise self._map_registration_error(error)

        user = result.unwrap()
        return UserResponse(
            id=str(user.id),
            email=str(user.email),
            full_name=user.full_name,
            status=user.status.value,
            email_verified=user.email_verified,
            roles=user.roles,
            created_at=user.created_at,
        )

    async def authenticate(self, request: AuthenticationRequest) -> AuthenticationResponse:
        """Handle authentication request.

        Args:
            request: Authentication request

        Returns:
            Authentication response with tokens

        Raises:
            HTTPException: If authentication fails
        """
        result = await self._authenticate_user.execute(
            email=request.email,
            password=request.password,
        )

        if result.is_err():
            error = result.unwrap_err()
            raise self._map_authentication_error(error)

        auth_result = result.unwrap()
        return AuthenticationResponse(
            access_token=str(auth_result.access_token),
            refresh_token=str(auth_result.refresh_token),
            token_type="bearer",
            expires_in=1800,  # 30 minutes
            user=UserResponse(
                id=auth_result.user_id,
                email=auth_result.email,
                full_name="",  # Would need to be added to AuthenticationResult
                status="active",
                email_verified=True,
                roles=auth_result.roles,
                created_at=None,  # Would need to be added to AuthenticationResult
            ),
        )

    async def refresh(self, request: RefreshTokenRequest) -> RefreshTokenResponse:
        """Handle token refresh request.

        Args:
            request: Refresh token request

        Returns:
            New access token

        Raises:
            HTTPException: If token refresh fails
        """
        result = await self._refresh_token.execute(
            refresh_token_string=request.refresh_token,
        )

        if result.is_err():
            error = result.unwrap_err()
            raise self._map_refresh_error(error)

        new_token = result.unwrap()
        return RefreshTokenResponse(
            access_token=str(new_token),
            token_type="bearer",
            expires_in=1800,  # 30 minutes
        )

    def _map_registration_error(self, error: RegistrationError) -> HTTPException:
        """Map registration error to HTTP exception.

        Args:
            error: Registration error

        Returns:
            HTTP exception
        """
        error_map = {
            RegistrationError.INVALID_EMAIL: (
                status.HTTP_400_BAD_REQUEST,
                "Invalid email format",
            ),
            RegistrationError.EMAIL_ALREADY_EXISTS: (
                status.HTTP_409_CONFLICT,
                "Email already registered",
            ),
            RegistrationError.INVALID_PASSWORD: (
                status.HTTP_400_BAD_REQUEST,
                "Password must be at least 8 characters",
            ),
            RegistrationError.REPOSITORY_ERROR: (
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Internal server error",
            ),
        }

        status_code, detail = error_map.get(
            error, (status.HTTP_500_INTERNAL_SERVER_ERROR, "Unknown error")
        )
        return HTTPException(status_code=status_code, detail=detail)

    def _map_authentication_error(self, error: AuthenticationError) -> HTTPException:
        """Map authentication error to HTTP exception.

        Args:
            error: Authentication error

        Returns:
            HTTP exception
        """
        error_map = {
            AuthenticationError.INVALID_EMAIL: (
                status.HTTP_400_BAD_REQUEST,
                "Invalid email format",
            ),
            AuthenticationError.INVALID_CREDENTIALS: (
                status.HTTP_401_UNAUTHORIZED,
                "Invalid email or password",
            ),
            AuthenticationError.USER_NOT_FOUND: (
                status.HTTP_401_UNAUTHORIZED,
                "Invalid email or password",
            ),
            AuthenticationError.USER_CANNOT_LOGIN: (
                status.HTTP_403_FORBIDDEN,
                "Account is not active or email not verified",
            ),
            AuthenticationError.REPOSITORY_ERROR: (
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Internal server error",
            ),
        }

        status_code, detail = error_map.get(
            error, (status.HTTP_500_INTERNAL_SERVER_ERROR, "Unknown error")
        )
        return HTTPException(status_code=status_code, detail=detail)

    def _map_refresh_error(self, error: RefreshTokenError) -> HTTPException:
        """Map refresh token error to HTTP exception.

        Args:
            error: Refresh token error

        Returns:
            HTTP exception
        """
        error_map = {
            RefreshTokenError.INVALID_TOKEN: (
                status.HTTP_401_UNAUTHORIZED,
                "Invalid or expired refresh token",
            ),
            RefreshTokenError.USER_NOT_FOUND: (
                status.HTTP_401_UNAUTHORIZED,
                "User not found",
            ),
            RefreshTokenError.USER_CANNOT_LOGIN: (
                status.HTTP_403_FORBIDDEN,
                "Account is not active",
            ),
            RefreshTokenError.REPOSITORY_ERROR: (
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Internal server error",
            ),
        }

        status_code, detail = error_map.get(
            error, (status.HTTP_500_INTERNAL_SERVER_ERROR, "Unknown error")
        )
        return HTTPException(status_code=status_code, detail=detail)

