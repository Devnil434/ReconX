from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RecoverRecon"
    app_env: str = "development"
    debug: bool = True

    database_url: str
    redis_url: str

    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_webhook_secret: str = ""

    openai_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()