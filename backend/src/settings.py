from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env",),
        env_prefix="",
        case_sensitive=False,
        extra="ignore"  # Ignore extra env variables not defined in the model
    )

    app_name: str = "Kubo Backend"
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000

    database_url: str = "postgresql://kubo_user:password@127.0.0.1:5432/kubodb"

    secret_key: str = "change-me"
    password_scheme: str = "bcrypt"

    session_cookie_name: str = "kubo_session"
    session_expire_minutes: int = 60 * 24 * 30  # 30 days
    cookie_secure: bool = False
    samesite: str = "lax"  # lax | none | strict

    cors_origins: List[AnyHttpUrl] | List[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    cerebras_api_key: str | None = None

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value: List[AnyHttpUrl] | List[str] | str) -> List[str] | List[AnyHttpUrl]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()


