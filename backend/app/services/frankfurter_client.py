import httpx
from datetime import date, timedelta
from decimal import Decimal

from app.schemas.frankfurter import FrankfurterRatesResponse


class FrankfurterClient:
    BASE_URL = "https://api.frankfurter.dev/v2"

    async def get_latest_rates(
        self, base: str = "USD", quotes: list[str] | None = None
    ) -> list[dict]:
        params: dict = {"base": base}
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
            raise Exception(f"Failed to fetch latest rates: {str(e)}")

    async def get_historical_rates(
        self,
        base: str,
        quotes: list[str],
        from_date: date,
        to_date: date,
    ) -> list[dict]:
        params: dict = {
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
            raise Exception(f"Failed to fetch historical rates: {str(e)}")

    async def get_supported_currencies(self) -> list[dict]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.BASE_URL}/currencies")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"Failed to fetch currencies: {str(e)}")

    async def get_7day_history(
        self, base: str = "USD", quotes: list[str] | None = None
    ) -> dict[str, list[dict]]:
        to_date = date.today()
        from_date = to_date - timedelta(days=7)
        data = await self.get_historical_rates(
            base=base,
            quotes=quotes or [],
            from_date=from_date,
            to_date=to_date,
        )

        history: dict[str, list[dict]] = {}
        for item in data:
            currency = item["quote"]
            if currency not in history:
                history[currency] = []
            history[currency].append(
                {"date": item["date"], "rate": item["rate"]}
            )
        return history


frankfurter_client = FrankfurterClient()