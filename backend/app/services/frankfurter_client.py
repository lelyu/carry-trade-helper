import httpx
from typing import List, Dict, Optional
from datetime import date
from app.core.config import settings


class FrankfurterClient:
    BASE_URL = "https://api.frankfurter.dev/v2"
    
    async def get_latest_rates(
        self,
        base: str = "USD",
        quotes: Optional[List[str]] = None
    ) -> Dict:
        params = {"base": base}
        if quotes:
            params["quotes"] = ",".join(quotes)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/rates", params=params)
            response.raise_for_status()
            return response.json()
    
    async def get_historical_rates(
        self,
        base: str,
        quotes: List[str],
        from_date: date,
        to_date: date
    ) -> List[Dict]:
        params = {
            "base": base,
            "quotes": ",".join(quotes),
            "from": from_date.isoformat(),
            "to": to_date.isoformat()
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/rates", params=params)
            response.raise_for_status()
            return response.json()
    
    async def get_supported_currencies(self) -> List[Dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/currencies")
            response.raise_for_status()
            return response.json()
    
    async def get_rate(self, base: str, target: str, rate_date: Optional[date] = None) -> Dict:
        params = {}
        if rate_date:
            params["date"] = rate_date.isoformat()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/rate/{base}/{target}", params=params)
            response.raise_for_status()
            return response.json()


frankfurter_client = FrankfurterClient()