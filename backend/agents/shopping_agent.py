"""
FinVerse AI — Shopping Intelligence Agent (VISIBLE SEARCH MODE)
Performs live web search, extracts prices, compares ratings, recommends best value.
All queries are displayed to the user in real-time.
"""

import logging
import re
from backend.agents.base_agent import BaseAgent
from backend.models.agent_response import AvatarState

logger = logging.getLogger(__name__)


class ShoppingAgent(BaseAgent):
    """
    Agent 4: Shopping Intelligence (Visible Mode)
    - Performs live web search with visible queries
    - Extracts product prices from results
    - Compares ratings across retailers
    - Recommends best value
    - Checks against user's budget
    """

    def __init__(self, llm_provider=None, search_tool=None, budget_calculator=None):
        super().__init__(
            name="shopping_agent",
            description="Live web search for product comparison with visible execution",
            llm_provider=llm_provider,
        )
        self.search_tool = search_tool
        self.budget_calculator = budget_calculator

    async def execute(self, state: dict) -> dict:
        """Execute visible shopping search pipeline."""
        query = state.get("query", "")
        user_profile = state.get("user_profile")

        # Step 1: Display the plan
        self.emit_event("plan", {
            "message": "Shopping Intelligence Plan:",
            "steps": [
                "Search across retailers for product",
                "Extract prices and ratings",
                "Compare options",
                "Check against your budget",
                "Provide recommendation"
            ]
        }, AvatarState.THINKING)

        # Step 2: Generate search queries
        product_name = await self._extract_product(query)

        search_queries = [
            f"{product_name} price Amazon India",
            f"{product_name} price Flipkart",
            f"{product_name} best deal India 2025",
        ]

        # Step 3: Display search queries BEFORE execution (VISIBLE MODE)
        for sq in search_queries:
            self.emit_event("search", {
                "query": sq,
                "status": "queued",
                "icon": "🔎"
            }, AvatarState.SEARCHING)

        # Step 4: Execute searches
        search_results = []
        if self.search_tool:
            for sq in search_queries:
                self.emit_event("search", {
                    "query": sq,
                    "status": "executing",
                    "icon": "🔍"
                }, AvatarState.SEARCHING)

                result = await self.search_tool.search(sq, num_results=3)
                search_results.append(result)

                self.emit_event("search", {
                    "query": sq,
                    "status": "completed",
                    "results_count": len(result.get("results", [])),
                    "provider": result.get("provider", "unknown"),
                    "icon": "✅"
                }, AvatarState.SEARCHING)
        else:
            # Demo mode with simulated results
            search_results = self._get_demo_results(product_name)
            for sq in search_queries:
                self.emit_event("search", {
                    "query": sq,
                    "status": "completed",
                    "results_count": 3,
                    "provider": "demo",
                    "icon": "✅"
                }, AvatarState.SEARCHING)

        # Step 5: Extract and structure price data
        self.emit_event("thinking", {
            "message": "Extracting prices and ratings from search results..."
        }, AvatarState.ANALYZING)

        price_comparison = await self._extract_prices(product_name, search_results, query)

        self.emit_event("result", {
            "type": "price_comparison",
            "data": price_comparison
        }, AvatarState.ANALYZING)

        # Step 6: Check budget
        budget_check = None
        if user_profile and price_comparison.get("prices"):
            lowest_price = min(p.get("price", float('inf')) for p in price_comparison["prices"])
            if self.budget_calculator:
                budget_check = self.budget_calculator.check_purchase_affordability(
                    user_profile, lowest_price, "shopping"
                )
                self.emit_event("tool_call", {
                    "tool": "budget_calculator",
                    "action": "purchase_check",
                    "amount": lowest_price,
                    "result": budget_check,
                }, AvatarState.ANALYZING)

        # Step 7: Generate recommendation
        recommendation = await self._generate_recommendation(
            product_name, price_comparison, budget_check, query
        )

        self.emit_event("result", {
            "agent": self.name,
            "product": product_name,
            "recommendation": recommendation,
            "price_comparison": price_comparison,
            "budget_check": budget_check,
        }, AvatarState.RECOMMENDING)

        state["shopping_results"] = {
            "product": product_name,
            "price_comparison": price_comparison,
            "recommendation": recommendation,
            "budget_check": budget_check,
        }
        state["agents_used"] = state.get("agents_used", []) + [self.name]
        state["events"] = state.get("events", []) + self.get_events()
        return state

    async def _extract_product(self, query: str) -> str:
        """Extract the product name from the user's query."""
        if self.llm:
            prompt = f"Extract just the product name from this query. Reply with ONLY the product name, nothing else:\n\n\"{query}\""
            result = await self.think(prompt)
            return result.strip().strip('"\'')
        # Fallback: use query as-is
        return query.replace("buy", "").replace("find", "").replace("search", "").replace("price", "").strip()

    async def _extract_prices(self, product: str, search_results: list, query: str) -> dict:
        """Extract structured price data from search results."""
        # Combine all search snippets
        all_snippets = []
        for result_group in search_results:
            for r in result_group.get("results", []):
                all_snippets.append(f"[{r.get('title', '')}] {r.get('snippet', '')} - {r.get('url', '')}")

        if self.llm and all_snippets:
            system_prompt = """Extract product prices from these search results.
Return a structured list in this exact format:
RETAILER: name
PRICE: number (in INR, numbers only)
RATING: number out of 5
URL: url

List each retailer on separate lines. If price is not found, write PRICE: N/A.
Only include real data found in the search results. Never fabricate prices."""

            prompt = f"Product: {product}\n\nSearch Results:\n" + "\n".join(all_snippets[:10])
            result = await self.think(prompt, system_prompt)

            return {
                "product": product,
                "prices": self._parse_price_response(result),
                "raw_analysis": result,
            }

        # Demo fallback
        return self._get_demo_prices(product)

    def _parse_price_response(self, response: str) -> list:
        """Parse LLM response into structured price data."""
        prices = []
        lines = response.strip().split("\n")

        current = {}
        for line in lines:
            line = line.strip()
            if line.upper().startswith("RETAILER:"):
                if current.get("retailer"):
                    prices.append(current)
                current = {"retailer": line.split(":", 1)[1].strip()}
            elif line.upper().startswith("PRICE:"):
                price_str = line.split(":", 1)[1].strip()
                price_num = re.sub(r'[^\d.]', '', price_str)
                try:
                    current["price"] = float(price_num) if price_num else 0
                except ValueError:
                    current["price"] = 0
            elif line.upper().startswith("RATING:"):
                rating_str = line.split(":", 1)[1].strip()
                rating_num = re.sub(r'[^\d.]', '', rating_str.split("/")[0].split("out")[0])
                try:
                    current["rating"] = float(rating_num) if rating_num else 0
                except ValueError:
                    current["rating"] = 0
            elif line.upper().startswith("URL:"):
                current["url"] = line.split(":", 1)[1].strip()

        if current.get("retailer"):
            prices.append(current)

        return prices

    async def _generate_recommendation(self, product: str, price_data: dict, budget_check: dict, query: str) -> str:
        """Generate final shopping recommendation."""
        if not self.llm:
            return "Unable to generate recommendation (LLM not available)"

        system_prompt = """You are the Shopping Intelligence Agent.
Provide a concise, structured recommendation based on real data.
Include: best value pick, price comparison, budget impact.
Never hallucinate prices. Only recommend based on observed data."""

        prompt = f"""Product: {product}
User Query: {query}

Price Data:
{price_data.get('raw_analysis', 'No price data available')}

Budget Impact:
{f"Affordable: {budget_check['affordable']}" if budget_check else 'Budget check not available'}
{f"Discretionary Balance: ₹{budget_check['discretionary_balance']:,.0f}" if budget_check else ''}
{f"Warnings: {', '.join(budget_check.get('warnings', []))}" if budget_check and budget_check.get('warnings') else ''}

Provide a clear recommendation with the best value option."""

        return await self.think(prompt, system_prompt)

    def _get_demo_results(self, product: str) -> list:
        """Generate demo search results when no search API is configured."""
        return [
            {"provider": "demo", "query": f"{product} price Amazon", "results": [
                {"title": f"{product} - Amazon.in", "snippet": f"Buy {product} at best price on Amazon India. Fast delivery available.", "url": "https://amazon.in"},
            ]},
            {"provider": "demo", "query": f"{product} price Flipkart", "results": [
                {"title": f"{product} - Flipkart", "snippet": f"{product} available at competitive prices on Flipkart.", "url": "https://flipkart.com"},
            ]},
        ]

    def _get_demo_prices(self, product: str) -> dict:
        """Return demo price comparison data."""
        return {
            "product": product,
            "prices": [
                {"retailer": "Amazon", "price": 72990, "rating": 4.6, "url": "https://amazon.in"},
                {"retailer": "Flipkart", "price": 73499, "rating": 4.5, "url": "https://flipkart.com"},
                {"retailer": "Croma", "price": 74000, "rating": 4.4, "url": "https://croma.com"},
            ],
            "raw_analysis": f"Demo price comparison for {product}",
        }
