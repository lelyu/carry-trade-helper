import asyncio

from deepagents import create_deep_agent

from app.core.config import settings
from app.services.tavily_client import internet_search
from app.services.frankfurter_client import frankfurter_client
from app.services.fred_client import fred_client


def get_exchange_rate(base: str, target: str) -> dict:
    """
    Get current exchange rate

    Args:
        base: Base currency code
        target: Target currency code

    Returns:
        Dictionary with exchange rate information
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = pool.submit(asyncio.run, frankfurter_client.get_rate(base, target)).result()
    else:
        result = asyncio.run(frankfurter_client.get_rate(base, target))

    return {
        "base": base,
        "target": target,
        "rate": result.get("rate", 0),
        "date": result.get("date"),
    }


def get_interest_rate(currency: str) -> dict:
    """
    Get current interest rate for a currency

    Args:
        currency: Currency code

    Returns:
        Dictionary with interest rate information
    """
    CURRENCY_TO_COUNTRY = {
        "USD": "USA",
        "EUR": "EUR",
        "GBP": "GBR",
        "JPY": "JPN",
        "CHF": "CHF",
        "AUD": "AUD",
        "CAD": "CAD",
        "NZD": "NZD",
        "CNY": "CHN",
        "HKD": "HKG",
    }

    country = CURRENCY_TO_COUNTRY.get(currency, currency)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            results = pool.submit(asyncio.run, fred_client.get_interest_rates([country])).result()
    else:
        results = asyncio.run(fred_client.get_interest_rates([country]))

    if results:
        return {
            "currency": currency,
            "country": country,
            "rate": results[0].get("rate", 0),
            "date": results[0].get("date"),
        }

    return {"currency": currency, "rate": None, "error": "Rate not found"}


carry_trade_system_prompt = """You are an expert carry trade analyst. Your job is to:

1. Analyze current exchange rates and interest rate differentials
2. Research economic conditions using web search
3. Identify carry trade opportunities and risks
4. Provide actionable trading recommendations

You have access to:
- `internet_search`: Search for financial news and analysis
- `get_exchange_rate`: Get current exchange rates
- `get_interest_rate`: Get current central bank rates

Always consider:
- Interest rate differentials between currency pairs
- Currency stability and volatility
- Economic indicators and central bank policies
- Geopolitical risks
- Historical performance

When analyzing carry trades:
1. Calculate the interest rate spread
2. Assess currency risk (volatility, trend)
3. Research recent economic developments
4. Consider transaction costs
5. Provide risk-adjusted recommendations

Format your responses clearly with:
- Current rates summary
- Key findings from research
- Trading recommendation (Long/Short/Neutral)
- Risk assessment
- Entry/Exit points if applicable

Always emphasize risk management and never provide financial advice as guaranteed outcomes."""


_carry_trade_agent: object | None = None


def get_carry_trade_agent():
    """Get or create the carry trade agent (lazy initialization)"""
    global _carry_trade_agent

    if _carry_trade_agent is None:
        _carry_trade_agent = create_deep_agent(
            model="gemini-3-flash-preview",
            tools=[internet_search, get_exchange_rate, get_interest_rate],
            system_prompt=carry_trade_system_prompt,
        )

    return _carry_trade_agent
