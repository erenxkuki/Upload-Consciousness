"""Application settings loaded from environment."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="UCC_", extra="ignore")

    env: str = "development"
    log_level: str = "INFO"
    database_url: str = "sqlite+aiosqlite:///./ucc_dev.db"
    jwt_secret: str = "change-me-in-production-use-32-plus-random-bytes"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    redis_url: str = ""
    node_id: str = "node-local-001"
    node_role: str = "identity_authority"


@lru_cache
def get_settings() -> Settings:
    return Settings()
