"""FastAPI configuration."""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # App
    APP_NAME: str = "GrabOn BNPL API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]

    # MCP Server
    MCP_SERVER_URL: str = "http://localhost:8001"

    # Redis (optional)
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600  # 1 hour

    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 500

    # PayU LazyPay Integration
    PAYU_SANDBOX_URL: str = "https://sandbox.payu.in"
    PAYU_MERCHANT_KEY: str = os.getenv("PAYU_MERCHANT_KEY", "gtKFFx")  # Sandbox test key
    PAYU_MERCHANT_SALT: str = os.getenv("PAYU_MERCHANT_SALT", "4R38IvwiV57FwVpsgOvTXBdLE4tHUXFW")  # Sandbox salt
    PAYU_MODE: str = "sandbox"  # "sandbox" or "production"
    PAYU_ENABLED: bool = os.getenv("PAYU_ENABLED", "true").lower() == "true"

    # API Base URL (for PayU callbacks)
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
