import httpx
from typing import List, Dict


class DBnomicsClient:
    BASE_URL = "https://api.db.nomics.world/v22"
    
    async def get_interest_rates(
        self,
        country_codes: List[str],
        rate_type: str = "policy_rate"
    ) -> List[Dict]:
        results = []
        
        country_provider_map = {
            "USA": ("FED", "FED/IRS/FED_FUNDS_RATE"),
            "EUR": ("ECB", "ECB/IRS/MAIN_REFINANCING_OPERATIONS"),
            "GBR": ("BOE", "BOE/IRS/UK_BANK_RATE"),
            "JPN": ("BOJ", "BOJ/IRS/POLICY_BALANCE_RATE"),
            "CHF": ("SNB", "SNB/IRS/LEADING_RATE"),
            "AUD": ("RBA", "RBA/IRS/CASH_RATE"),
            "CAD": ("BOC", "BOC/IRS/TARGET_RATE"),
            "NZD": ("RBNZ", "RBNZ/IRS/OFFICIAL_CASH_RATE"),
            "CHN": ("PBOC", "PBOC/IRS/LENDING_RATE"),
            "HKG": ("HKMA", "HKMA/IRS/BASE_RATE"),
        }
        
        for country in country_codes:
            if country in country_provider_map:
                provider, series_code = country_provider_map[country]
                
                params = {
                    "series_ids": series_code
                }
                
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(
                            f"{self.BASE_URL}/series",
                            params=params,
                            timeout=30.0
                        )
                        response.raise_for_status()
                        data = response.json()
                        
                        if data.get("series") and data["series"].get("docs"):
                            latest = data["series"]["docs"][0]
                            results.append({
                                "country_code": country,
                                "currency_code": country[:3] if len(country) >= 3 else country,
                                "rate": float(latest.get("value", 0)),
                                "rate_type": rate_type,
                                "date": latest.get("period"),
                                "provider_code": provider
                            })
                except Exception as e:
                    print(f"Error fetching interest rate for {country}: {e}")
                    continue
        
        return results
    
    async def get_providers(self) -> List[Dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/providers")
            response.raise_for_status()
            return response.json()


dbnomics_client = DBnomicsClient()