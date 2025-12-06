"""User repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports import IUserRepository
from src.domain.entities import User, UserStatus
from src.domain.value_objects import Email, PasswordHash, UserId
from src.infrastructure.database.models import UserModel


class UserRepository(IUserRepository):
    """PostgreSQL implementation of user repository.

    Implements the IUserRepository port defined in the application layer.
    Handles mapping between domain entities and database models.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize user repository.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def find_by_id(self, user_id: UserId) -> User | None:
        """Find user by ID.

        Args:
            user_id: User identifier

        Returns:
            User if found, None otherwise
        """
        stmt = select(UserModel).where(UserModel.id == str(user_id))
        result = await self._session.execute(stmt)
        user_model = result.scalar_one_or_none()

        return self._to_entity(user_model) if user_model else None

    async def find_by_email(self, email: Email) -> User | None:
        """Find user by email.

        Args:
            email: User email

        Returns:
            User if found, None otherwise
        """
        stmt = select(UserModel).where(UserModel.email == str(email))
        result = await self._session.execute(stmt)
        user_model = result.scalar_one_or_none()

        return self._to_entity(user_model) if user_model else None

    async def save(self, user: User) -> None:
        """Save user (create or update).

        Args:
            user: User entity to save
        """
        # Check if user exists
        stmt = select(UserModel).where(UserModel.id == str(user.id))
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing user
            existing.email = str(user.email)
            existing.password_hash = str(user.password_hash)
            existing.full_name = user.full_name
            existing.status = user.status.value
            existing.email_verified = user.email_verified
            existing.last_login_at = user.last_login_at
            existing.updated_at = user.updated_at
            existing.roles = user.roles
        else:
            # Create new user
            user_model = self._to_model(user)
            self._session.add(user_model)

        await self._session.commit()

    async def delete(self, user_id: UserId) -> None:
        """Delete user by ID.

        Args:
            user_id: User identifier
        """
        stmt = select(UserModel).where(UserModel.id == str(user_id))
        result = await self._session.execute(stmt)
        user_model = result.scalar_one_or_none()

        if user_model:
            await self._session.delete(user_model)
            await self._session.commit()

    async def exists_by_email(self, email: Email) -> bool:
        """Check if user exists by email.

        Args:
            email: User email

        Returns:
            True if user exists, False otherwise
        """
        stmt = select(UserModel.id).where(UserModel.email == str(email))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def _to_entity(self, model: UserModel) -> User:
        """Convert database model to domain entity.

        Args:
            model: Database model

        Returns:
            Domain entity
        """
        return User(
            id=UserId.from_string(model.id),
            email=Email(value=model.email),
            password_hash=PasswordHash(value=model.password_hash),
            full_name=model.full_name,
            status=UserStatus(model.status),
            email_verified=model.email_verified,
            last_login_at=model.last_login_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            roles=model.roles or [],
        )

    def _to_model(self, entity: User) -> UserModel:
        """Convert domain entity to database model.

        Args:
            entity: Domain entity

        Returns:
            Database model
        """
        return UserModel(
            id=str(entity.id),
            email=str(entity.email),
            password_hash=str(entity.password_hash),
            full_name=entity.full_name,
            status=entity.status.value,
            email_verified=entity.email_verified,
            last_login_at=entity.last_login_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            roles=entity.roles,
        )

