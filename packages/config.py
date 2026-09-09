from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AEGIS_",
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    env: Literal["development", "test", "staging", "production"] = "development"
    incident_store: Literal["memory", "sql"] = "memory"
    database_url: str = "sqlite+pysqlite:///./aegis.db"
    autoremediation_enabled: bool = False
    log_level: str = "INFO"
    page_size_max: int = Field(default=100, ge=1, le=500)

    @model_validator(mode="after")
    def production_safety(self) -> "Settings":
        if self.env == "production" and self.incident_store == "memory":
            raise ValueError("production cannot use the in-memory incident store")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
