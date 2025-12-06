"""FastAPI routes for authentication."""

from fastapi import APIRouter, Depends, status

from src.adapters.controllers import AuthController
from src.adapters.dtos import (
    AuthenticationRequest,
    AuthenticationResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterUserRequest,
    UserResponse,
)
from src.infrastructure.api.dependencies import get_auth_controller

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user account with email and password",
)
async def register(
    request: RegisterUserRequest,
    controller: AuthController = Depends(get_auth_controller),
) -> UserResponse:
    """Register new user endpoint.

    Args:
        request: Registration request
        controller: Auth controller

    Returns:
        Created user information
    """
    return await controller.register(request)


@router.post(
    "/login",
    response_model=AuthenticationResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user",
    description="Authenticate user and receive access and refresh tokens",
)
async def login(
    request: AuthenticationRequest,
    controller: AuthController = Depends(get_auth_controller),
) -> AuthenticationResponse:
    """Login endpoint.

    Args:
        request: Authentication request
        controller: Auth controller

    Returns:
        Authentication response with tokens
    """
    return await controller.authenticate(request)


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get a new access token using a refresh token",
)
async def refresh_token(
    request: RefreshTokenRequest,
    controller: AuthController = Depends(get_auth_controller),
) -> RefreshTokenResponse:
    """Refresh token endpoint.

    Args:
        request: Refresh token request
        controller: Auth controller

    Returns:
        New access token
    """
    return await controller.refresh(request)

