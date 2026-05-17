from pydantic import BaseModel
from datetime import date as date_type


class ExchangeRateItem(BaseModel):
    target_currency: str
    rate: float
    date: date_type
    trend_7d: float | None = None


class ExchangeRateListResponse(BaseModel):
    base: str
    as_of: date_type | None = None
    rates: list[ExchangeRateItem]
    history_7d: dict[str, list[dict[str, str | float]]] | None = None


class InterestRateItem(BaseModel):
    country_code: str
    currency_code: str
    country_name: str
    rate: float
    date: date_type | None = None
    trend_7d: float | None = None


class InterestRateListResponse(BaseModel):
    as_of: date_type | None = None
    rates: list[InterestRateItem]
    history_7d: dict[str, list[dict[str, str | float]]] | None = None