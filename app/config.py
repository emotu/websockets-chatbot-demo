from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[".env", ".env.local"], env_file_encoding="utf-8", extra="ignore"
    )

    # Database
    DATABASE_URL: str
    DATABASE_ECHO: bool = True

    # Writer AI
    WRITER_API_KEY: str


@lru_cache
def get_settings():
    _settings = Settings()

    return _settings


settings = get_settings()
