from typing import Literal
from tavily import TavilyClient
from app.core.config import settings
from langchain.tools import tool


tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)


@tool(parse_docstring=True)
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "finance",
    include_raw_content: bool = False,
) -> dict:
    """
    Run a web search for financial news and analysis

    Args:
        query: Search query string
        max_results: Maximum number of results to return
        topic: Search topic category
        include_raw_content: Whether to include raw content

    Returns:
        Dictionary with search results
    """
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


def get_financial_news(query: str, max_results: int = 10) -> list[dict]:
    """
    Get financial news articles

    Args:
        query: Search query
        max_results: Number of results

    Returns:
        List of news articles
    """
    results = internet_search(query=query, max_results=max_results, topic="news")

    return results.get("results", [])
