"""Base entity class for domain entities."""

from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class BaseEntity(ABC):
    """Base class for all domain entities.

    Entities are objects that have an identity and lifecycle.
    Two entities with the same ID are considered the same entity,
    even if their attributes differ.

    Attributes:
        id: Unique identifier for the entity
        created_at: Timestamp when entity was created
        updated_at: Timestamp when entity was last updated
    """

    id: Any  # Can be UUID, int, or custom ID value object
    created_at: datetime
    updated_at: datetime

    def __eq__(self, other: object) -> bool:
        """Two entities are equal if they have the same ID.

        Args:
            other: Another object to compare with

        Returns:
            True if entities have the same ID, False otherwise
        """
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Entities are hashed by their ID.

        Returns:
            Hash of the entity ID
        """
        return hash(self.id)

