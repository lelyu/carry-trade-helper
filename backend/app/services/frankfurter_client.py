import httpx
from datetime import date
from app.core.config import settings


class FrankfurterClient:
    BASE_URL = "https://api.frankfurter.dev/v2"

    async def get_latest_rates(
        self, base: str = "USD", quotes: list[str] | None = None
    ) -> dict:
        params = {"base": base}
        if quotes:
            params["quotes"] = ",".join(quotes)

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/rates", params=params)
            response.raise_for_status()
            return response.json()

    async def get_historical_rates(
        self, base: str, quotes: list[str], from_date: date, to_date: date
    ) -> list[dict]:
        params = {
            "base": base,
            "quotes": ",".join(quotes),
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/rates", params=params)
            response.raise_for_status()
            return response.json()

    async def get_supported_currencies(self) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/currencies")
            response.raise_for_status()
            return response.json()

    async def get_rate(
        self, base: str, target: str, rate_date: date | None = None
    ) -> dict:
        params = {}
        if rate_date:
            params["date"] = rate_date.isoformat()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/rate/{base}/{target}", params=params
            )
            response.raise_for_status()
            return response.json()


frankfurter_client = FrankfurterClient()
