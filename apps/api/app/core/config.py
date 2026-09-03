from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "ReconX"
    database_url: str = "postgresql+psycopg://reconx:reconx_dev_password@localhost:5432/reconx"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:3000,https://reconx-phi.vercel.app"

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        if isinstance(v, str):
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+psycopg://", 1)
            elif v.startswith("postgresql://") and not v.startswith("postgresql+"):
                return v.replace("postgresql://", "postgresql+psycopg://", 1)
        return v

    @field_validator("redis_url", mode="before")
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        if isinstance(v, str) and v.startswith("https://"):
            raise ValueError(
                "REDIS_URL must use the Redis protocol (e.g. 'rediss://default:password@host:6379' or 'redis://localhost:6379/0'), not the Upstash HTTPS REST URL."
            )
        return v

    razorpay_key_id: str | None = "rzp_test_TUHiDLDs9QGDld"
    razorpay_key_secret: str | None = "XXMgpzs4oCikbdE4b2aqq9a6"
    razorpay_webhook_secret: str | None = "22WNn-ET.Xaqncn"
    razorpay_mode: str = "test"

    # AI Configuration (Gemini)
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    # Legacy OpenAI fallback if provided
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    demo_mode: bool = True
    failure_injection: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
