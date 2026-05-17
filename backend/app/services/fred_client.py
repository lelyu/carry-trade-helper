import httpx
from datetime import date, timedelta
from decimal import Decimal

from app.core.config import settings


class FredClient:
    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    COUNTRY_SERIES_MAP: dict[str, str] = {
        "USA": "FEDFUNDS",
        "EUR": "ECBDFR",
        "GBR": "INTDSRGBM193N",
        "JPN": "IRSTCI01JPM156N",
        "CHE": "IRSTCI01CHM156N",
        "AUD": "IRSTCI01AUM156N",
        "CAN": "INTDSRCAM193N",
        "NZL": "IRSTCI01NZM156N",
        "CHN": "INTDSRCNM193N",
        "HKG": "INTDSRHKM193N",
    }

    COUNTRY_CURRENCY_MAP: dict[str, str] = {
        "USA": "USD",
        "EUR": "EUR",
        "GBR": "GBP",
        "JPN": "JPY",
        "CHE": "CHF",
        "AUD": "AUD",
        "CAN": "CAD",
        "NZL": "NZD",
        "CHN": "CNY",
        "HKG": "HKD",
    }

    ALL_COUNTRIES = list(COUNTRY_SERIES_MAP.keys())

    async def get_interest_rates(
        self, country_codes: list[str]
    ) -> list[dict]:
        results = []

        for country in country_codes:
            if country not in self.COUNTRY_SERIES_MAP:
                continue

            series_id = self.COUNTRY_SERIES_MAP[country]

            try:
                async with httpx.AsyncClient() as client:
                    params: dict = {
                        "series_id": series_id,
                        "api_key": settings.FRED_API_KEY,
                        "file_type": "json",
                        "sort_order": "desc",
                        "limit": 1,
                    }

                    response = await client.get(
                        self.BASE_URL, params=params, timeout=30.0
                    )
                    response.raise_for_status()
                    data = response.json()

                    if data.get("observations"):
                        latest = data["observations"][0]
                        rate_value = float(latest.get("value", 0))
                        rate_date = latest.get("date")

                        results.append(
                            {
                                "country_code": country,
                                "currency_code": self.COUNTRY_CURRENCY_MAP.get(
                                    country, country[:3]
                                ),
                                "rate": rate_value,
                                "rate_type": "policy_rate",
                                "date": rate_date,
                                "source": "fred",
                            }
                        )

            except Exception as e:
                print(f"Error fetching rate for {country}: {e}")
                continue

        return results

    async def get_historical_rates(
        self, country_codes: list[str], from_date: date, to_date: date
    ) -> dict[str, list[dict]]:
        history: dict[str, list[dict]] = {}

        for country in country_codes:
            if country not in self.COUNTRY_SERIES_MAP:
                continue

            series_id = self.COUNTRY_SERIES_MAP[country]

            try:
                async with httpx.AsyncClient() as client:
                    params: dict = {
                        "series_id": series_id,
                        "api_key": settings.FRED_API_KEY,
                        "file_type": "json",
                        "observation_start": from_date.isoformat(),
                        "observation_end": to_date.isoformat(),
                        "sort_order": "asc",
                    }

                    response = await client.get(
                        self.BASE_URL, params=params, timeout=30.0
                    )
                    response.raise_for_status()
                    data = response.json()

                    observations = data.get("observations", [])
                    country_history = []

                    for obs in observations:
                        value = obs.get("value", ".")
                        if value == ".":
                            continue
                        country_history.append(
                            {
                                "date": obs.get("date"),
                                "rate": float(value),
                            }
                        )

                    if country_history:
                        history[country] = country_history

            except Exception as e:
                print(f"Error fetching historical rates for {country}: {e}")
                continue

        return history

    async def get_7day_history(
        self, country_codes: list[str]
    ) -> dict[str, list[dict]]:
        to_date = date.today()
        from_date = to_date - timedelta(days=365)
        raw = await self.get_historical_rates(country_codes, from_date, to_date)
        result: dict[str, list[dict]] = {}
        for country, points in raw.items():
            seen_rates: set[float] = set()
            deduped: list[dict] = []
            for p in points:
                rate_key = round(p["rate"], 4)
                if rate_key not in seen_rates:
                    seen_rates.add(rate_key)
                    deduped.append(p)
            result[country] = deduped
        return result


fred_client = FredClient()