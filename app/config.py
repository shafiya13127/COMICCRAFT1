from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    gemini_api_key: str

    gemini_model: str = "gemini-2.5-flash"

    app_name: str = "ComicCraft - AI Comic Story Creator"

    max_panels: int = 8

    default_panels: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()