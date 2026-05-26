from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "SAFE-NET"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/safenet"
    REDIS_URL: str = "redis://redis:6379/0"
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    AFRICASTALKING_API_KEY: str | None = None
    AFRICASTALKING_USERNAME: str | None = None
    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    FCM_SERVER_KEY: str | None = None
    MESH_GATEWAY_HMAC_SECRET: str = "change-me"
    STARLINK_SSID: str | None = None
    SMS_SENDER_ID: str = "SAFE-NET"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
