"""Configuration for aggregation service."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    """Redis configuration."""

    host: str = Field(default="localhost")
    port: int = Field(default=6379)
    db: int = Field(default=0)

    @property
    def url(self) -> str:
        """Get Redis URL."""
        return f"redis://{self.host}:{self.port}/{self.db}"

    model_config = SettingsConfigDict(env_prefix="REDIS_")


class Settings(BaseSettings):
    """Application settings."""

    service_name: str = Field(default="aggregation-service")
    log_level: str = Field(default="INFO")
    cache_ttl_seconds: int = Field(default=300)

    redis: RedisSettings = Field(default_factory=RedisSettings)

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()

