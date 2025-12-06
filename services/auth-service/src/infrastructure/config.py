"""Configuration using Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration."""

    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    name: str = Field(default="auth_db", description="Database name")
    user: str = Field(default="auth_user", description="Database user")
    password: str = Field(default="auth_password", description="Database password")

    @property
    def url(self) -> str:
        """Get database URL.

        Returns:
            PostgreSQL async connection URL
        """
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    model_config = SettingsConfigDict(env_prefix="DATABASE_")


class RedisSettings(BaseSettings):
    """Redis configuration."""

    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, description="Redis port")
    db: int = Field(default=0, description="Redis database number")
    password: str | None = Field(default=None, description="Redis password")

    @property
    def url(self) -> str:
        """Get Redis URL.

        Returns:
            Redis connection URL
        """
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"

    model_config = SettingsConfigDict(env_prefix="REDIS_")


class JWTSettings(BaseSettings):
    """JWT configuration."""

    secret_key: str = Field(..., description="JWT secret key")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7, description="Refresh token expiration in days"
    )

    model_config = SettingsConfigDict(env_prefix="JWT_")


class Settings(BaseSettings):
    """Application settings."""

    service_name: str = Field(default="auth-service", description="Service name")
    log_level: str = Field(default="INFO", description="Log level")
    debug: bool = Field(default=False, description="Debug mode")

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
    )


def get_settings() -> Settings:
    """Get application settings.

    Returns:
        Application settings instance
    """
    return Settings()

