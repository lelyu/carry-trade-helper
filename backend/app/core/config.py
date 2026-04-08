from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    RESEND_API_KEY: str
    GOOGLE_API_KEY: str
    TAVILY_API_KEY: str
    SECRET_KEY: str
    FRONTEND_URL: str = "http://localhost:3000"
    EMAIL_DOMAIN: str = "localhost"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MAGIC_LINK_EXPIRE_MINUTES: int = 15

    SUPPORTED_CURRENCIES: list[str] = [
        "EUR",
        "GBP",
        "JPY",
        "CHF",
        "AUD",
        "CAD",
        "NZD",
        "CNY",
        "HKD",
    ]

    SUPPORTED_CURRENCY_PAIRS: list[str] = [
        "EUR/USD",
        "GBP/USD",
        "USD/JPY",
        "USD/CHF",
        "AUD/USD",
        "USD/CAD",
        "NZD/USD",
        "USD/CNY",
        "USD/HKD",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
