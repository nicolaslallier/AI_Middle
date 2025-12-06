"""Configuration for gateway service."""

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

    service_name: str = Field(default="gateway-service")
    log_level: str = Field(default="INFO")
    auth_service_url: str = Field(default="http://localhost:8001")
    aggregation_service_url: str = Field(default="http://localhost:8003")
    rate_limit_per_minute: int = Field(default=60)
    circuit_breaker_threshold: int = Field(default=5)

    redis: RedisSettings = Field(default_factory=RedisSettings)

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()

