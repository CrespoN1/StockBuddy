from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    # Database — Railway provides postgresql://, we need postgresql+asyncpg://
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/stockbuddy"

    @property
    def async_database_url(self) -> str:
        """Return database URL with asyncpg driver, converting if needed."""
        url = self.database_url
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth (Clerk)
    clerk_secret_key: str = ""
    clerk_jwks_url: str = ""

    # External APIs
    alpha_vantage_api_key: str = ""
    deepseek_api_key: str = ""
    fmp_api_key: str = ""
    massive_api_key: str = ""

    # API URLs
    deepseek_url: str = "https://api.deepseek.com/v1/chat/completions"
    alpha_vantage_base_url: str = "https://www.alphavantage.co/query"
    massive_base_url: str = "https://api.massive.com/v3/reference/tickers"

    # AI Settings
    ai_max_tokens: int = 2000
    ai_temperature: float = 0.3

    # CORS
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # Rate Limiting (slowapi format)
    general_rate_limit: str = "100/minute"
    ai_rate_limit: str = "10/minute"
    search_rate_limit: str = "30/minute"

    # Sentry
    sentry_dsn: str = ""

    def validate_production(self) -> None:
        """Validate that required settings are present in production."""
        if self.environment != "production":
            return

        required = {
            "database_url": self.database_url,
            "redis_url": self.redis_url,
            "clerk_jwks_url": self.clerk_jwks_url,
            "clerk_secret_key": self.clerk_secret_key,
            "deepseek_api_key": self.deepseek_api_key,
        }

        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError(
                f"Missing required production settings: {', '.join(missing)}"
            )


settings = Settings()
