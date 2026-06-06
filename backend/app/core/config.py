from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "Wellness Tracker API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "sqlite+aiosqlite:///./wellness.db"
    GEMINI_API_KEY: str = "dummy_key_if_not_set"

    # Auth — set a long random string in production (openssl rand -hex 32)
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Comma-separated list of frontend URLs for CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Gmail SMTP (use an App Password — https://myaccount.google.com/apppasswords)
    GMAIL_ADDRESS: str = ""
    GMAIL_APP_PASSWORD: str = ""

    STRESS_ALERT_THRESHOLD: float = 7.0
    ANXIETY_ALERT_THRESHOLD: float = 7.0

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
