"""Database session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.config import DatabaseSettings


class DatabaseSessionManager:
    """Manages database sessions and engine lifecycle."""

    def __init__(self, database_url: str) -> None:
        """Initialize database session manager.

        Args:
            database_url: Database connection URL
        """
        self._engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    async def close(self) -> None:
        """Close database engine."""
        if self._engine:
            await self._engine.dispose()

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session.

        Yields:
            Database session
        """
        async with self._session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


# Global session manager instance
_session_manager: DatabaseSessionManager | None = None


def init_db(settings: DatabaseSettings) -> None:
    """Initialize database session manager.

    Args:
        settings: Database settings
    """
    global _session_manager
    _session_manager = DatabaseSessionManager(settings.url)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency.

    Yields:
        Database session

    Raises:
        RuntimeError: If database not initialized
    """
    if _session_manager is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    async for session in _session_manager.get_session():
        yield session


async def close_db() -> None:
    """Close database connections."""
    if _session_manager:
        await _session_manager.close()

