from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    api_token: str = Field(default="dev-token-change-me", alias="LICENSE_API_TOKEN")
    signing_secret: str = Field(default="dev-signing-secret", alias="LICENSE_SIGNING_SECRET")
    default_grace_hours: int = Field(default=72, alias="LICENSE_GRACE_HOURS")


settings = Settings()
