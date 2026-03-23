from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "myPowerCoach API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"
    password_salt: str = "myPowerCoach-dev-salt"

    model_config = SettingsConfigDict(
        env_prefix="MYPOWERCOACH_",
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
