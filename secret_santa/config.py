"""Configuration file."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlmodel import create_engine


class Settings(BaseSettings):
    DB_URL: str
    DEBUG: bool = False

    MAX_DRAW_GENERATION_ATTEMPTS: int = 50

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

engine = create_engine(settings.DB_URL, echo=settings.DEBUG)
