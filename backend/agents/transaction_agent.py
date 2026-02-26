"""
FinVerse AI — Transaction Intelligence Agent
Categorizes transactions, detects anomalies, tracks behavioral drift.
"""

import logging
from backend.agents.base_agent import BaseAgent
from backend.models.agent_response import AvatarState

logger = logging.getLogger(__name__)


class TransactionAgent(BaseAgent):
    """
    Agent 1: Transaction Intelligence
    - Categorizes transactions
    - Detects anomalies (amount, time, merchant)
    - Detects behavioral drift
    - Updates user financial profile
    """

    def __init__(self, llm_provider=None):
        super().__init__(
            name="transaction_agent",
            description="Analyzes transactions for patterns, anomalies, and behavioral drift",
            llm_provider=llm_provider,
        )

    async def execute(self, state: dict) -> dict:
        """Analyze transactions in the current state."""
        query = state.get("query", "")
        transactions = state.get("transactions", [])
        user_profile = state.get("user_profile")

        self.emit_event("thinking", {
            "message": "Analyzing transaction patterns and behavioral data..."
        }, AvatarState.ANALYZING)

        # Build transaction summary
        if transactions:
            txn_summary = self._summarize_transactions(transactions)
        else:
            txn_summary = "No recent transactions available."

        # Build analysis prompt
        system_prompt = """You are a Transaction Intelligence Agent for FinVerse AI.
Your role is to:
1. Analyze transaction patterns and spending behavior
2. Detect anomalies and unusual spending
3. Identify behavioral drift (changes in spending patterns)
4. Provide insights about financial health

Always respond with structured, actionable insights.
Never fabricate transaction data. Only analyze what is provided."""

        prompt = f"""User Query: {query}

Transaction Summary:
{txn_summary}

User Profile:
- Monthly Income: ₹{user_profile.monthly_income:,.0f} if user_profile else 'N/A'
- Total Balance: ₹{user_profile.total_balance:,.0f} if user_profile else 'N/A'

Analyze the transactions and provide insights. Include:
1. Spending pattern analysis
2. Any anomalies detected
3. Category-wise breakdown
4. Behavioral observations"""

        analysis = await self.think(prompt, system_prompt)

        self.emit_event("result", {
            "agent": self.name,
            "analysis": analysis,
            "transaction_count": len(transactions),
        }, AvatarState.RECOMMENDING)

        state["transaction_analysis"] = analysis
        state["agents_used"] = state.get("agents_used", []) + [self.name]
        state["events"] = state.get("events", []) + self.get_events()
        return state

    def _summarize_transactions(self, transactions: list) -> str:
        """Create a text summary of recent transactions."""
        if not transactions:
            return "No transactions."

        lines = []
        total_spent = 0
        total_income = 0
        categories = {}

        for txn in transactions[-20:]:  # Last 20 transactions
            amount = txn.get("amount", 0)
            cat = txn.get("category", "other")
            merchant = txn.get("merchant", "Unknown")
            is_credit = txn.get("is_credit", False)

            if is_credit:
                total_income += amount
                lines.append(f"  + ₹{amount:,.0f} from {merchant} ({cat})")
            else:
                total_spent += amount
                lines.append(f"  - ₹{amount:,.0f} at {merchant} ({cat})")

            categories[cat] = categories.get(cat, 0) + (amount if not is_credit else 0)

        summary = f"Recent Transactions ({len(transactions)} total):\n"
        summary += "\n".join(lines[:10])
        summary += f"\n\nTotal Spent: ₹{total_spent:,.0f}"
        summary += f"\nTotal Income: ₹{total_income:,.0f}"
        summary += "\n\nCategory Breakdown:"
        for cat, amount in sorted(categories.items(), key=lambda x: -x[1])[:5]:
            summary += f"\n  {cat}: ₹{amount:,.0f}"

        return summary
