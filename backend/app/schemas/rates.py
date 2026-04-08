from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from uuid import UUID


class ExchangeRateBase(BaseModel):
    base_currency: str
    target_currency: str
    rate: Decimal
    date: date
    source: str = "frankfurter"


class ExchangeRateResponse(ExchangeRateBase):
    id: UUID
    created_at: date

    class Config:
        from_attributes = True


class ExchangeRateListResponse(BaseModel):
    rates: list[ExchangeRateResponse]
    count: int


class InterestRateBase(BaseModel):
    country_code: str
    currency_code: str
    rate: Decimal
    rate_type: str | None = None
    date: date
    source: str = "dbnomics"
    provider_code: str | None = None


class InterestRateResponse(InterestRateBase):
    id: UUID
    created_at: date

    class Config:
        from_attributes = True


class InterestRateListResponse(BaseModel):
    rates: list[InterestRateResponse]
    count: int
