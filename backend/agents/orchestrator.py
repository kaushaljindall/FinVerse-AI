"""
FinVerse AI — LangGraph Multi-Agent Orchestrator
Stateful multi-agent workflow graph that routes queries to the appropriate agents.
"""

import asyncio
import logging
import time
from typing import Optional

from backend.agents.transaction_agent import TransactionAgent
from backend.agents.budget_agent import BudgetAgent
from backend.agents.compliance_agent import ComplianceAgent
from backend.agents.shopping_agent import ShoppingAgent
from backend.agents.rag_agent import RAGAgent
from backend.agents.explanation_agent import ExplanationAgent
from backend.models.agent_response import AgentResponse, AgentEvent, AvatarState
from backend.llm.provider import LLMProvider
from backend.tools.web_search import WebSearchTool
from backend.tools.budget_calculator import BudgetCalculator

logger = logging.getLogger(__name__)


# Query intent classification keywords
INTENT_KEYWORDS = {
    "shopping": ["buy", "purchase", "price", "cost", "deal", "compare", "shop", "order", "find me", "cheapest", "best value", "how much"],
    "transaction": ["transaction", "spending", "spent", "payment", "transfer", "expense", "income", "salary"],
    "budget": ["budget", "afford", "save", "savings", "limit", "overspend", "financial health", "balance"],
    "compliance": ["compliance", "regulation", "rule", "legal", "fraud", "suspicious", "aml", "kyc"],
    "rag": ["policy", "document", "clause", "agreement", "terms", "conditions", "insurance", "loan", "contract"],
}


class AgentOrchestrator:
    """
    LangGraph-style multi-agent orchestrator.
    Routes queries to appropriate agents and synthesizes responses.
    """

    def __init__(self, settings):
        self.settings = settings
        self.llm = LLMProvider(settings)
        self.search_tool = WebSearchTool(settings)
        self.budget_calculator = BudgetCalculator()

        # Initialize agents
        self.agents = {
            "transaction": TransactionAgent(llm_provider=self.llm),
            "budget": BudgetAgent(llm_provider=self.llm),
            "compliance": ComplianceAgent(llm_provider=self.llm),
            "shopping": ShoppingAgent(
                llm_provider=self.llm,
                search_tool=self.search_tool,
                budget_calculator=self.budget_calculator,
            ),
            "rag": RAGAgent(llm_provider=self.llm),
            "explanation": ExplanationAgent(llm_provider=self.llm),
        }

        # Hybrid retriever (initialized lazily)
        self._retriever = None

    def set_retriever(self, retriever):
        """Set the hybrid retriever for RAG agent."""
        self._retriever = retriever
        self.agents["rag"].retriever = retriever

    async def process_query(self, query: str, user_profile=None, transactions=None, event_callback=None) -> AgentResponse:
        """
        Process a user query through the multi-agent graph.

        Args:
            query: User's question/request
            user_profile: User's financial profile
            transactions: Recent transaction data
            event_callback: Async callback for streaming events to frontend

        Returns:
            AgentResponse with full results
        """
        start_time = time.time()

        # Initialize shared state
        state = {
            "query": query,
            "user_profile": user_profile,
            "transactions": transactions or [],
            "agents_used": [],
            "events": [],
        }

        # Step 1: Classify intent
        intents = self._classify_intent(query)
        logger.info(f"🎯 Classified intents: {intents}")

        # Emit routing event
        routing_event = AgentEvent(
            type="routing",
            agent="orchestrator",
            content={
                "message": f"Routing query to agents: {', '.join(intents)}",
                "intents": intents,
            },
            avatar_state=AvatarState.THINKING,
        )
        if event_callback:
            await event_callback(routing_event)

        # Step 2: Execute the agent graph based on intents
        # Shopping queries get special visible search treatment
        if "shopping" in intents:
            state = await self._execute_shopping_flow(state, event_callback)
        else:
            # Execute relevant agents in parallel where possible
            tasks = []
            if "transaction" in intents:
                tasks.append(("transaction", self.agents["transaction"].execute(state.copy())))
            if "budget" in intents:
                tasks.append(("budget", self.agents["budget"].execute(state.copy())))
            if "rag" in intents:
                tasks.append(("rag", self.agents["rag"].execute(state.copy())))

            # Execute parallel agents
            if tasks:
                results = await asyncio.gather(
                    *[task for _, task in tasks],
                    return_exceptions=True
                )
                for (name, _), result in zip(tasks, results):
                    if isinstance(result, Exception):
                        logger.error(f"Agent {name} failed: {result}")
                    else:
                        # Merge state from each agent
                        for key, value in result.items():
                            if key == "agents_used":
                                state["agents_used"] = list(set(state.get("agents_used", []) + value))
                            elif key == "events":
                                state["events"] = state.get("events", []) + value
                            else:
                                state[key] = value

                    # Stream events
                    if event_callback and isinstance(result, dict):
                        for event in result.get("events", []):
                            await event_callback(event)

            # Always run compliance on non-shopping queries if they involve money
            if "compliance" in intents or any(i in intents for i in ["transaction", "budget"]):
                state = await self.agents["compliance"].execute(state)
                if event_callback:
                    for event in state.get("events", [])[-3:]:
                        await event_callback(event)

        # Step 3: Always run explanation agent last
        state = await self.agents["explanation"].execute(state)
        if event_callback:
            for event in state.get("events", [])[-2:]:
                await event_callback(event)

        # Build final response
        processing_time = time.time() - start_time

        response = AgentResponse(
            query=query,
            response=state.get("final_response", "I was unable to process your query. Please try again."),
            agents_used=state.get("agents_used", []),
            events=state.get("events", []),
            citations=state.get("citations", []),
            avatar_state=AvatarState.IDLE,
            processing_time=round(processing_time, 2),
        )

        logger.info(f"✅ Query processed in {processing_time:.2f}s using agents: {response.agents_used}")
        return response

    async def _execute_shopping_flow(self, state: dict, event_callback=None) -> dict:
        """Execute the shopping-specific flow with visible search mode."""
        # Run shopping agent (visible search)
        state = await self.agents["shopping"].execute(state)

        if event_callback:
            for event in state.get("events", []):
                await event_callback(event)

        # Run budget check
        state = await self.agents["budget"].execute(state)

        if event_callback:
            for event in state.get("events", [])[-3:]:
                await event_callback(event)

        # Run compliance on shopping recommendations
        state = await self.agents["compliance"].execute(state)

        return state

    def _classify_intent(self, query: str) -> list[str]:
        """
        Classify the query intent to determine which agents to invoke.
        Uses keyword matching — can be replaced with LLM classification.
        """
        query_lower = query.lower()
        intents = []

        for intent, keywords in INTENT_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                intents.append(intent)

        # Default: route to explanation agent (handles general financial queries)
        if not intents:
            intents = ["general"]

        return intents
