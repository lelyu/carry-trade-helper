from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    FRED_API_KEY: str
    FRONTEND_URL: str = "http://localhost:3000"
    CACHE_TTL_SECONDS: int = 3600

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

    COUNTRY_NAMES: dict[str, str] = {
        "USA": "United States",
        "EUR": "Euro Area",
        "GBR": "United Kingdom",
        "JPN": "Japan",
        "CHE": "Switzerland",
        "AUD": "Australia",
        "CAN": "Canada",
        "NZL": "New Zealand",
        "CHN": "China",
        "HKG": "Hong Kong",
    }

    CURRENCY_NAMES: dict[str, str] = {
        "USD": "US Dollar",
        "EUR": "Euro",
        "GBP": "British Pound",
        "JPY": "Japanese Yen",
        "CHF": "Swiss Franc",
        "AUD": "Australian Dollar",
        "CAD": "Canadian Dollar",
        "NZD": "New Zealand Dollar",
        "CNY": "Chinese Yuan",
        "HKD": "Hong Kong Dollar",
    }

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()