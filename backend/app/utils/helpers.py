def format_currency_pair(base: str, target: str) -> str:
    """Format currency pair as BASE/TARGET"""
    return f"{base}/{target}"


def parse_currency_pair(pair: str) -> tuple:
    """Parse currency pair string into base and target"""
    parts = pair.split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid currency pair format: {pair}")
    return parts[0], parts[1]


def calculate_carry_potential(
    base_rate: float,
    target_rate: float,
    exchange_rate: float
) -> dict:
    """Calculate carry trade potential"""
    interest_differential = abs(target_rate - base_rate)
    
    annualized_return = interest_differential
    
    return {
        "interest_differential": interest_differential,
        "annualized_return": annualized_return,
        "favorable": interest_differential > 0
    }