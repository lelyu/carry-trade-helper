import httpx
from datetime import date
from app.core.config import settings
from app.schemas.frankfurter import FrankfurterRatesResponse


class FrankfurterClient:
    BASE_URL = "https://api.frankfurter.dev/v2"

    async def get_latest_rates(
        self, base: str = "USD", quotes: list[str] | None = None
    ) -> list[dict]:
        params = {"base": base}
        if quotes:
            params["quotes"] = ",".join(quotes)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.BASE_URL}/rates", params=params)
                response.raise_for_status()
                data = response.json()
                validated = FrankfurterRatesResponse(rates=data)
                return [item.model_dump() for item in validated.rates]
        except httpx.HTTPError as e:
            raise Exception(
                f"Failed to fetch latest rates from Frankfurter API: {str(e)}"
            )

    async def get_historical_rates(
        self, base: str, quotes: list[str], from_date: date, to_date: date
    ) -> list[dict]:
        params = {
            "base": base,
            "quotes": ",".join(quotes),
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.BASE_URL}/rates", params=params)
                response.raise_for_status()
                data = response.json()
                validated = FrankfurterRatesResponse(rates=data)
                return [item.model_dump() for item in validated.rates]
        except httpx.HTTPError as e:
            raise Exception(
                f"Failed to fetch historical rates from Frankfurter API: {str(e)}"
            )

    async def get_supported_currencies(self) -> list[dict]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.BASE_URL}/currencies")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise Exception(
                f"Failed to fetch supported currencies from Frankfurter API: {str(e)}"
            )

    async def get_rate(
        self, base: str, target: str, rate_date: date | None = None
    ) -> dict:
        params = {}
        if rate_date:
            params["date"] = rate_date.isoformat()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/rate/{base}/{target}", params=params
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"Failed to fetch rate from Frankfurter API: {str(e)}")


frankfurter_client = FrankfurterClient()
