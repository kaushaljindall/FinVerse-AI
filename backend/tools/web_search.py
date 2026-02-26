"""
FinVerse AI — Web Search Tool
Multi-fallback search: Tavily → SerpAPI → Structured scraping
All queries are visible to the user (Visible Search Mode).
"""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class WebSearchTool:
    """
    Multi-fallback web search.
    Primary: Tavily → Secondary: SerpAPI → Tertiary: Basic scraping
    """

    def __init__(self, settings):
        self.settings = settings

    async def search(self, query: str, num_results: int = 5) -> dict:
        """
        Search the web with multi-layer fallback.
        Returns: {provider, query, results: [{title, url, snippet, price?}]}
        """
        # Try Tavily first
        if self.settings.TAVILY_API_KEY:
            try:
                result = await self._search_tavily(query, num_results)
                if result:
                    return {"provider": "tavily", "query": query, "results": result}
            except Exception as e:
                logger.warning(f"Tavily search failed: {e}")

        # Fallback to SerpAPI
        if self.settings.SERPAPI_API_KEY:
            try:
                result = await self._search_serpapi(query, num_results)
                if result:
                    return {"provider": "serpapi", "query": query, "results": result}
            except Exception as e:
                logger.warning(f"SerpAPI search failed: {e}")

        # Final fallback: return no results gracefully
        logger.warning("All search providers failed")
        return {
            "provider": "none",
            "query": query,
            "results": [],
            "error": "All search providers unavailable. Please configure TAVILY_API_KEY or SERPAPI_API_KEY."
        }

    async def _search_tavily(self, query: str, num_results: int) -> list:
        """Search using Tavily API."""
        from tavily import TavilyClient

        client = TavilyClient(api_key=self.settings.TAVILY_API_KEY)
        response = await asyncio.to_thread(
            client.search,
            query=query,
            max_results=num_results,
            search_depth="advanced",
        )

        results = []
        for item in response.get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", "")[:300],
                "score": item.get("score", 0),
            })
        return results

    async def _search_serpapi(self, query: str, num_results: int) -> list:
        """Search using SerpAPI."""
        import serpapi

        params = {
            "q": query,
            "num": num_results,
            "api_key": self.settings.SERPAPI_API_KEY,
            "engine": "google",
        }

        response = await asyncio.to_thread(serpapi.search, params)

        results = []
        for item in response.get("organic_results", [])[:num_results]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", "")[:300],
                "position": item.get("position", 0),
            })
        return results

    async def multi_search(self, queries: list[str], num_results: int = 3) -> list[dict]:
        """Execute multiple search queries in parallel (for visible search mode)."""
        tasks = [self.search(q, num_results) for q in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        search_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                search_results.append({
                    "provider": "error",
                    "query": queries[i],
                    "results": [],
                    "error": str(result)
                })
            else:
                search_results.append(result)

        return search_results
