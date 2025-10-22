"""
Application settings and configuration
Environment variables를 통해 설정 관리
"""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str

    # Database
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # AI Services
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_TRACING_V2: bool = False

    # External APIs
    GOOGLE_MAPS_API_KEY: str
    MAPBOX_ACCESS_TOKEN: str
    SKYSCANNER_API_KEY: str = ""
    BOOKING_COM_AFFILIATE_ID: str = ""
    AGODA_API_KEY: str = ""

    # Task Queue
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TTL_PLACES: int = 60 * 15  # 15 minutes
    REDIS_TTL_FLIGHTS: int = 60 * 5  # 5 minutes
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AUTH: str = "5/minute"

    # Metrics
    METRICS_ENABLED: bool = True
    SENTRY_DSN: str | None = None
    SENTRY_SAMPLE_RATE: float = 0.1
    POSTHOG_API_KEY: str | None = None
    POSTHOG_HOST: str = "https://app.posthog.com"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

    # PDF Export
    PDF_POOL_SIZE: int = 2
    PDF_RENDER_TIMEOUT: int = 60  # seconds
    PDF_BUCKET_NAME: str = "travel-plan-pdfs"
    PDF_SIGNED_URL_TTL: int = 3600  # seconds
    PDF_BRAND_NAME: str = "TravelTailor"
    PDF_INCLUDE_PREVIEW: bool = True
    PDF_TEMPLATE_LOCALE: str = "ko-KR"
    PDF_STORAGE_FOLDER: str = "itineraries"
    PDF_PUBLIC_BASE_URL: Optional[str] = None

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False

    # Cookies / session (web)
    SESSION_COOKIE_NAME: str = "tt_session"
    SESSION_COOKIE_DOMAIN: str | None = None
    SESSION_COOKIE_SECURE: bool = False
    SESSION_COOKIE_SAMESITE: str = "lax"

    class Config:
        env_file = ".env"
        case_sensitive = True

    def model_post_init(self, __context: dict[str, object]) -> None:
        if self.APP_ENV == "production":
            self.SESSION_COOKIE_SECURE = True


# Global settings instance
settings = Settings()
