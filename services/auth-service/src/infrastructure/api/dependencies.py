"""Dependency injection for FastAPI."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.controllers import AuthController
from src.adapters.repositories import UserRepository
from src.application.ports import IPasswordHasher, ITokenService, IUserRepository
from src.application.use_cases import AuthenticateUser, RefreshToken, RegisterUser
from src.infrastructure.config import get_settings
from src.infrastructure.database.session import get_db_session
from src.infrastructure.security.jwt_service import JWTTokenService
from src.infrastructure.security.password_hasher import BcryptPasswordHasher


# Repository dependencies
def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> IUserRepository:
    """Get user repository dependency.

    Args:
        session: Database session

    Returns:
        User repository instance
    """
    return UserRepository(session)


# Service dependencies
def get_password_hasher() -> IPasswordHasher:
    """Get password hasher dependency.

    Returns:
        Password hasher instance
    """
    return BcryptPasswordHasher()


def get_token_service() -> ITokenService:
    """Get token service dependency.

    Returns:
        Token service instance
    """
    settings = get_settings()
    return JWTTokenService(settings.jwt)


# Use case dependencies
def get_register_user_use_case(
    user_repository: IUserRepository = Depends(get_user_repository),
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
) -> RegisterUser:
    """Get register user use case dependency.

    Args:
        user_repository: User repository
        password_hasher: Password hasher

    Returns:
        RegisterUser use case instance
    """
    return RegisterUser(user_repository, password_hasher)


def get_authenticate_user_use_case(
    user_repository: IUserRepository = Depends(get_user_repository),
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
    token_service: ITokenService = Depends(get_token_service),
) -> AuthenticateUser:
    """Get authenticate user use case dependency.

    Args:
        user_repository: User repository
        password_hasher: Password hasher
        token_service: Token service

    Returns:
        AuthenticateUser use case instance
    """
    return AuthenticateUser(user_repository, password_hasher, token_service)


def get_refresh_token_use_case(
    user_repository: IUserRepository = Depends(get_user_repository),
    token_service: ITokenService = Depends(get_token_service),
) -> RefreshToken:
    """Get refresh token use case dependency.

    Args:
        user_repository: User repository
        token_service: Token service

    Returns:
        RefreshToken use case instance
    """
    return RefreshToken(user_repository, token_service)


# Controller dependencies
def get_auth_controller(
    register_user: RegisterUser = Depends(get_register_user_use_case),
    authenticate_user: AuthenticateUser = Depends(get_authenticate_user_use_case),
    refresh_token: RefreshToken = Depends(get_refresh_token_use_case),
) -> AuthController:
    """Get auth controller dependency.

    Args:
        register_user: Register user use case
        authenticate_user: Authenticate user use case
        refresh_token: Refresh token use case

    Returns:
        AuthController instance
    """
    return AuthController(register_user, authenticate_user, refresh_token)

