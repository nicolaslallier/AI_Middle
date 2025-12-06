"""User entity."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from common.domain import BaseEntity
from src.domain.exceptions import InvalidUserStatusTransitionError, UserAlreadyDeletedException
from src.domain.value_objects import Email, PasswordHash, UserId


class UserStatus(str, Enum):
    """User account status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


@dataclass
class User(BaseEntity):
    """User entity representing a user account.

    Encapsulates user business rules and invariants.
    Users can be in different statuses with allowed transitions.

    Attributes:
        id: Unique user identifier
        email: User's email address
        password_hash: Hashed password
        full_name: User's full name
        status: Current account status
        created_at: When user was created
        updated_at: When user was last updated
        email_verified: Whether email has been verified
        last_login_at: Last login timestamp
        roles: List of user roles
    """

    id: UserId
    created_at: datetime
    updated_at: datetime
    email: Email
    password_hash: PasswordHash
    full_name: str
    status: UserStatus
    email_verified: bool = False
    last_login_at: datetime | None = None
    roles: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        email: Email,
        password_hash: PasswordHash,
        full_name: str,
        roles: list[str] | None = None,
    ) -> "User":
        """Factory method for creating new users.

        Args:
            email: User's email address
            password_hash: Hashed password
            full_name: User's full name
            roles: Optional list of roles

        Returns:
            New User entity with ACTIVE status
        """
        now = datetime.now(timezone.utc)
        return cls(
            id=UserId.generate(),
            created_at=now,
            updated_at=now,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            status=UserStatus.ACTIVE,
            email_verified=False,
            last_login_at=None,
            roles=roles or ["user"],
        )

    def can_login(self) -> bool:
        """Check if user can login.

        Business rule: Only active users with verified emails can login.

        Returns:
            True if user can login, False otherwise
        """
        return self.status == UserStatus.ACTIVE and self.email_verified

    def mark_login(self) -> None:
        """Mark that user has logged in.

        Updates last login timestamp.

        Raises:
            UserAlreadyDeletedException: If user is deleted
        """
        self._ensure_not_deleted()
        self.last_login_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def verify_email(self) -> None:
        """Mark email as verified.

        Raises:
            UserAlreadyDeletedException: If user is deleted
        """
        self._ensure_not_deleted()
        self.email_verified = True
        self.updated_at = datetime.now(timezone.utc)

    def change_password(self, new_password_hash: PasswordHash) -> None:
        """Change user password.

        Args:
            new_password_hash: New hashed password

        Raises:
            UserAlreadyDeletedException: If user is deleted
        """
        self._ensure_not_deleted()
        object.__setattr__(self, "password_hash", new_password_hash)
        self.updated_at = datetime.now(timezone.utc)

    def activate(self) -> None:
        """Activate user account.

        Allowed transitions: INACTIVE -> ACTIVE, SUSPENDED -> ACTIVE

        Raises:
            InvalidUserStatusTransitionError: If transition not allowed
            UserAlreadyDeletedException: If user is deleted
        """
        self._ensure_not_deleted()
        if self.status not in [UserStatus.INACTIVE, UserStatus.SUSPENDED]:
            raise InvalidUserStatusTransitionError(self.status.value, UserStatus.ACTIVE.value)
        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.now(timezone.utc)

    def deactivate(self) -> None:
        """Deactivate user account.

        Allowed transition: ACTIVE -> INACTIVE

        Raises:
            InvalidUserStatusTransitionError: If transition not allowed
            UserAlreadyDeletedException: If user is deleted
        """
        self._ensure_not_deleted()
        if self.status != UserStatus.ACTIVE:
            raise InvalidUserStatusTransitionError(self.status.value, UserStatus.INACTIVE.value)
        self.status = UserStatus.INACTIVE
        self.updated_at = datetime.now(timezone.utc)

    def suspend(self) -> None:
        """Suspend user account.

        Allowed transition: ACTIVE -> SUSPENDED

        Raises:
            InvalidUserStatusTransitionError: If transition not allowed
            UserAlreadyDeletedException: If user is deleted
        """
        self._ensure_not_deleted()
        if self.status != UserStatus.ACTIVE:
            raise InvalidUserStatusTransitionError(self.status.value, UserStatus.SUSPENDED.value)
        self.status = UserStatus.SUSPENDED
        self.updated_at = datetime.now(timezone.utc)

    def delete(self) -> None:
        """Soft delete user account.

        Any status can transition to DELETED.
        """
        if self.status == UserStatus.DELETED:
            raise UserAlreadyDeletedException()
        self.status = UserStatus.DELETED
        self.updated_at = datetime.now(timezone.utc)

    def add_role(self, role: str) -> None:
        """Add a role to the user.

        Args:
            role: Role name to add

        Raises:
            UserAlreadyDeletedException: If user is deleted
        """
        self._ensure_not_deleted()
        if role not in self.roles:
            self.roles.append(role)
            self.updated_at = datetime.now(timezone.utc)

    def remove_role(self, role: str) -> None:
        """Remove a role from the user.

        Args:
            role: Role name to remove

        Raises:
            UserAlreadyDeletedException: If user is deleted
        """
        self._ensure_not_deleted()
        if role in self.roles:
            self.roles.remove(role)
            self.updated_at = datetime.now(timezone.utc)

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role.

        Args:
            role: Role name to check

        Returns:
            True if user has the role, False otherwise
        """
        return role in self.roles

    def _ensure_not_deleted(self) -> None:
        """Ensure user is not deleted.

        Raises:
            UserAlreadyDeletedException: If user is deleted
        """
        if self.status == UserStatus.DELETED:
            raise UserAlreadyDeletedException()

