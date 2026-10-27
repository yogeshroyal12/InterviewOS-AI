from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, read from environment variables or the .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "InterviewOS AI"
    environment: str = "development"
    database_url: str = "sqlite:///./interviewos.db"


@lru_cache
def get_settings() -> Settings:
    """Return one shared Settings object for the whole application."""
    return Settings()


settings = get_settings()