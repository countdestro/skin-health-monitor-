"""Application configuration from environment variables."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Backend settings loaded from environment."""

    # Database
    postgres_url: str = "postgresql+asyncpg://user:pass@localhost:5432/skin_monitor"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret: str = "change-me-32-byte-random-string-for-demo"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    # External services (for gateway orchestration)
    image_processor_url: str = "http://localhost:8001"
    ai_inference_url: str = "http://localhost:8002"

    # Limits
    max_image_size_mb: int = 10
    rate_limit_per_minute: int = 10

    # Storage
    image_store_backend: str = "local"  # 's3' or 'local'
    image_storage_path: str = "/tmp/skin_monitor_images"

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
