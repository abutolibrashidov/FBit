from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Bot Configuration
    BOT_TOKEN: str
    ADMIN_IDS: List[int] = []

    # Admin Auth
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "changeme"
    ADMIN_SECRET: str = "fbit_jwt_secret_key_change_in_prod"

    # App Configuration
    APP_NAME: str = "Telegram Social Platform"
    DEBUG: bool = False
    BASE_URL: str = "https://your-domain.vercel.app"

    # Database Configuration
    DATABASE_URL: str

    # Redis Configuration
    REDIS_URL: str

    # Modules Configuration
    ANONYMOUS_LINK_PREFIX: str = "https://t.me/bot?start=msg_"
    REFERRAL_LINK_PREFIX: str = "https://t.me/bot?start=ref_"

    # Local Settings
    LOG_LEVEL: str = "INFO"

settings = Settings()
