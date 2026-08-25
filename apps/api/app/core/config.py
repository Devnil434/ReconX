from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[4]
ROOT_ENV = ROOT_DIR / ".env"


class Settings(BaseSettings):
    app_name: str = "RecoverRecon"
    app_env: str = "development"
    debug: bool = True

    database_url: str = "postgresql+psycopg://reconx:reconx_dev_password@localhost:5432/reconx"
    redis_url: str = "redis://localhost:6379/0"

    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_webhook_secret: str = ""

    openai_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", "../../.env", str(ROOT_ENV)),
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()