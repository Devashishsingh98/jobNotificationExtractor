"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    supabase_database_url: str

    # Telegram Scraper (Telethon)
    telegram_api_id: int
    telegram_api_hash: str

    # Telegram Bot
    telegram_bot_token: str

    # Gemini
    google_api_key: str

    # Redis
    redis_url: str = "redis://localhost:6379"

    # App
    app_env: str = "development"
    secret_key: str = "change-this-in-production"

    # JWT
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 72

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
