"""Base value object class for domain value objects."""

from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject(ABC):
    """Base class for all value objects.

    Value objects are immutable objects that have no identity.
    Two value objects with the same attributes are considered equal.

    Value objects must be:
    - Immutable (frozen=True)
    - Equal by value, not identity
    - Side-effect free

    Example:
        >>> @dataclass(frozen=True)
        >>> class Email(ValueObject):
        ...     value: str
        ...
        ...     def __post_init__(self) -> None:
        ...         if "@" not in self.value:
        ...             raise ValueError("Invalid email")
        ...
        >>> email1 = Email("test@example.com")
        >>> email2 = Email("test@example.com")
        >>> email1 == email2  # True - same value
        >>> email1 is email2  # False - different objects
    """

    pass

