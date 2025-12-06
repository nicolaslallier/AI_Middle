"""Result monad for error handling without exceptions."""

from typing import Callable, Generic, TypeVar, Union

# Type variables for success and error types
T = TypeVar("T")  # Success type
E = TypeVar("E")  # Error type
U = TypeVar("U")  # Mapped success type


class Result(Generic[T, E]):
    """Result monad for functional error handling.

    A Result represents either success (Ok) or failure (Err).
    This allows handling errors without exceptions, making
    error paths explicit in the type system.

    Examples:
        >>> def divide(a: int, b: int) -> Result[float, str]:
        ...     if b == 0:
        ...         return Err("Division by zero")
        ...     return Ok(a / b)
        ...
        >>> result = divide(10, 2)
        >>> if result.is_ok():
        ...     print(f"Success: {result.unwrap()}")
        >>> else:
        ...     print(f"Error: {result.unwrap_err()}")
        Success: 5.0

        >>> result = divide(10, 0)
        >>> value = result.unwrap_or(0.0)
        >>> print(value)
        0.0
    """

    def __init__(self, value: Union[T, E], is_ok: bool) -> None:
        """Initialize Result.

        Args:
            value: The success or error value
            is_ok: True if this is a success result, False for error
        """
        self._value = value
        self._is_ok = is_ok

    def is_ok(self) -> bool:
        """Check if this is a success result.

        Returns:
            True if this is Ok, False if this is Err
        """
        return self._is_ok

    def is_err(self) -> bool:
        """Check if this is an error result.

        Returns:
            True if this is Err, False if this is Ok
        """
        return not self._is_ok

    def unwrap(self) -> T:
        """Get the success value.

        Returns:
            The success value

        Raises:
            ValueError: If this is an error result
        """
        if not self._is_ok:
            raise ValueError(f"Called unwrap() on an Err value: {self._value}")
        return self._value  # type: ignore

    def unwrap_err(self) -> E:
        """Get the error value.

        Returns:
            The error value

        Raises:
            ValueError: If this is a success result
        """
        if self._is_ok:
            raise ValueError(f"Called unwrap_err() on an Ok value: {self._value}")
        return self._value  # type: ignore

    def unwrap_or(self, default: T) -> T:
        """Get the success value or a default.

        Args:
            default: Default value to return if this is an error

        Returns:
            The success value if Ok, otherwise the default
        """
        if self._is_ok:
            return self._value  # type: ignore
        return default

    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        """Get the success value or compute from error.

        Args:
            func: Function to compute default from error value

        Returns:
            The success value if Ok, otherwise result of func(error)
        """
        if self._is_ok:
            return self._value  # type: ignore
        return func(self._value)  # type: ignore

    def map(self, func: Callable[[T], U]) -> "Result[U, E]":
        """Transform the success value.

        Args:
            func: Function to transform the success value

        Returns:
            New Result with transformed value if Ok, otherwise same Err
        """
        if self._is_ok:
            return Ok(func(self._value))  # type: ignore
        return Err(self._value)  # type: ignore

    def map_err(self, func: Callable[[E], U]) -> "Result[T, U]":
        """Transform the error value.

        Args:
            func: Function to transform the error value

        Returns:
            Same Ok if success, otherwise new Result with transformed error
        """
        if self._is_ok:
            return Ok(self._value)  # type: ignore
        return Err(func(self._value))  # type: ignore

    def and_then(self, func: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        """Chain operations that return Results (flatMap).

        Args:
            func: Function that takes success value and returns a Result

        Returns:
            Result of func if this is Ok, otherwise same Err
        """
        if self._is_ok:
            return func(self._value)  # type: ignore
        return Err(self._value)  # type: ignore

    def __repr__(self) -> str:
        """String representation of Result.

        Returns:
            String showing Ok or Err with value
        """
        if self._is_ok:
            return f"Ok({self._value!r})"
        return f"Err({self._value!r})"


def Ok(value: T) -> Result[T, E]:
    """Create a success Result.

    Args:
        value: The success value

    Returns:
        Result representing success
    """
    return Result(value, True)


def Err(error: E) -> Result[T, E]:
    """Create an error Result.

    Args:
        error: The error value

    Returns:
        Result representing failure
    """
    return Result(error, False)

