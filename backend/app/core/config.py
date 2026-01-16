from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Sports Commentary Analyzer"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database - Supabase PostgreSQL
    # Supports both local PostgreSQL and Supabase connection strings
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/sports_commentary"

    # Database connection pool settings (optimized for Supabase pooler)
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_PRE_PING: bool = True

    # Redis - Upstash or local
    # Supports both redis:// and rediss:// (TLS) protocols
    REDIS_URL: str = "redis://localhost:6379/0"

    # File uploads
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {"txt", "srt", "vtt", "json"}

    # CORS
    # Can be set as comma-separated string or list
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # Optional: HuggingFace token for private models or rate limits
    HUGGINGFACE_TOKEN: Optional[str] = None

    # Optional: Sentry DSN for error tracking
    SENTRY_DSN: Optional[str] = None

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string to list."""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.DEBUG

    @property
    def database_url_with_options(self) -> str:
        """Get database URL with SSL options for Supabase."""
        url = self.DATABASE_URL
        # Add SSL requirement for Supabase connections
        if "supabase" in url.lower() and "sslmode" not in url:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}sslmode=require"
        return url

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in environment


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Default settings instance
settings = get_settings()
