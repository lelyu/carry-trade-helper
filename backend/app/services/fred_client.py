import httpx
from datetime import date
from typing import List, Dict

from app.core.config import settings


class FredClient:
    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    COUNTRY_SERIES_MAP = {
        "USA": "FEDFUNDS",
        "EUR": "ECBDFR",
        "GBR": "INTDSRGBM193N",
        "JPN": "IRSTCI01JPM156N",
        "CHF": "IRSTCI01CHM156N",
        "AUD": "IRSTCI01AUM156N",
        "CAD": "INTDSRCAM193N",
        "NZD": "IRSTCI01NZM156N",
        "CHN": "INTDSRCNM193N",
        "HKG": "INTDSRHXM193N",  # May not always be available
    }

    COUNTRY_CURRENCY_MAP = {
        "USA": "USD",
        "EUR": "EUR",
        "GBR": "GBP",
        "JPN": "JPY",
        "CHF": "CHF",
        "AUD": "AUD",
        "CAD": "CAD",
        "NZD": "NZD",
        "CHN": "CNY",
        "HKG": "HKD",
    }

    async def get_interest_rates(
        self, country_codes: List[str], rate_type: str = "policy_rate"
    ) -> List[Dict]:
        """
        Fetch interest rates from FRED API for specified countries

        Args:
            country_codes: List of country codes (e.g., ['USA', 'EUR', 'GBR'])
            rate_type: Type of rate (default: 'policy_rate')

        Returns:
            List of dictionaries with interest rate data
        """
        results = []

        for country in country_codes:
            if country not in self.COUNTRY_SERIES_MAP:
                print(f"No FRED series mapping for country: {country}")
                continue

            series_id = self.COUNTRY_SERIES_MAP[country]

            try:
                async with httpx.AsyncClient() as client:
                    params = {
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
                                "rate_type": rate_type,
                                "date": rate_date,
                                "source": "fred",
                            }
                        )

            except Exception as e:
                print(
                    f"Error fetching interest rate for {country} (series: {series_id}): {e}"
                )
                continue

        return results


fred_client = FredClient()
