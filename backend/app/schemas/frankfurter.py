from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal


class FrankfurterRateItem(BaseModel):
    date: date
    base: str = Field(..., min_length=3, max_length=3)
    quote: str = Field(..., min_length=3, max_length=3)
    rate: Decimal = Field(..., gt=0)


class FrankfurterRatesResponse(BaseModel):
    rates: list[FrankfurterRateItem]
