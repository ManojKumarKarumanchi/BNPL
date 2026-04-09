"""FastAPI configuration."""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # App
    APP_NAME: str = os.getenv("APP_NAME", "GrabOn BNPL API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # CORS
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001,http://localhost:5173"
    ).split(",")

    # MCP Server
    MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", "http://localhost:8001")

    # # Redis (optional)
    # REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    # CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour

    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    RATE_LIMIT_PER_HOUR: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "500"))

    # PayU LazyPay Integration
    # NOTE: Uses mock PayU client by default (no real API calls)
    # To use real PayU sandbox:
    #   1. Get credentials from: https://dashboard.payu.in/merchant-onboarding
    #   2. Set PAYU_MERCHANT_KEY and PAYU_MERCHANT_SALT in .env
    #   3. System automatically switches from mock to real client
    PAYU_SANDBOX_URL: str = os.getenv("PAYU_SANDBOX_URL", "https://test.payu.in")
    PAYU_MERCHANT_KEY: str = os.getenv("PAYU_MERCHANT_KEY", "gtKFFx")  # Default = mock mode
    PAYU_MERCHANT_SALT: str = os.getenv("PAYU_MERCHANT_SALT", "4R38IvwiV57FwVpsgOvTXBdLE4tHUXFW")  # Default = mock mode
    PAYU_MODE: str = os.getenv("PAYU_MODE", "sandbox")
    # PayU enabled by default - uses mock client if no real credentials provided
    PAYU_ENABLED: bool = os.getenv("PAYU_ENABLED", "true").lower() == "true"

    # API Base URL (for PayU callbacks)
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")

    # AI Provider Configuration (for credit narratives)
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "claude")

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from environment


settings = Settings()
