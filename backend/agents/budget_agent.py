"""
FinVerse AI — Budget Guardian Agent
Tracks monthly spending, predicts savings depletion, prevents unsafe purchases.
"""

import logging
from backend.agents.base_agent import BaseAgent
from backend.models.agent_response import AvatarState
from backend.tools.budget_calculator import BudgetCalculator

logger = logging.getLogger(__name__)


class BudgetAgent(BaseAgent):
    """
    Agent 2: Budget Guardian
    - Tracks monthly spending against budgets
    - Predicts savings depletion
    - Prevents unsafe purchases
    - Suggests budget reallocation
    """

    def __init__(self, llm_provider=None):
        super().__init__(
            name="budget_agent",
            description="Tracks budgets, predicts savings, prevents unsafe spending",
            llm_provider=llm_provider,
        )
        self.calculator = BudgetCalculator()

    async def execute(self, state: dict) -> dict:
        """Evaluate budget health and purchase affordability."""
        query = state.get("query", "")
        user_profile = state.get("user_profile")
        purchase_amount = state.get("purchase_amount")
        purchase_category = state.get("purchase_category", "shopping")

        self.emit_event("thinking", {
            "message": "Evaluating budget health and spending limits..."
        }, AvatarState.ANALYZING)

        # Get financial summary
        financial_summary = self.calculator.get_financial_summary(user_profile)

        self.emit_event("tool_call", {
            "tool": "budget_calculator",
            "action": "financial_summary",
            "result": financial_summary,
        }, AvatarState.ANALYZING)

        # If there's a purchase to evaluate
        affordability = None
        if purchase_amount:
            affordability = self.calculator.check_purchase_affordability(
                user_profile, purchase_amount, purchase_category
            )
            self.emit_event("tool_call", {
                "tool": "budget_calculator",
                "action": "affordability_check",
                "amount": purchase_amount,
                "result": affordability,
            }, AvatarState.ANALYZING)

        # LLM analysis
        system_prompt = """You are the Budget Guardian Agent for FinVerse AI.
Your role is to:
1. Protect the user's financial health
2. Warn about unsafe spending
3. Suggest budget optimizations
4. Predict savings impact

Be concise and structured. Use bullet points.
If a purchase is risky, clearly explain why."""

        prompt = f"""User Query: {query}

Financial Summary:
- Monthly Income: ₹{financial_summary['monthly_income']:,.0f}
- Total Spent: ₹{financial_summary['total_spent']:,.0f}
- Discretionary Balance: ₹{financial_summary['discretionary_balance']:,.0f}
- Health Score: {financial_summary['health_score']['score']}/100 ({financial_summary['health_score']['label']})

Budget Status:
{chr(10).join(f"  {b['category']}: ₹{b['spent']:,.0f}/₹{b['limit']:,.0f} ({b['utilization_pct']}%)" for b in financial_summary['budgets'])}

{f'Purchase Evaluation: ₹{purchase_amount:,.0f} in {purchase_category}' if purchase_amount else 'No specific purchase to evaluate.'}
{f'Affordable: {affordability["affordable"]}' if affordability else ''}
{f'Warnings: {", ".join(affordability["warnings"])}' if affordability and affordability["warnings"] else ''}

Provide your budget analysis and recommendation."""

        analysis = await self.think(prompt, system_prompt)

        # Determine avatar state based on health
        if financial_summary['health_score']['score'] < 40:
            avatar_state = AvatarState.ALERT
        elif affordability and not affordability.get("affordable", True):
            avatar_state = AvatarState.ALERT
        else:
            avatar_state = AvatarState.RECOMMENDING

        self.emit_event("result", {
            "agent": self.name,
            "analysis": analysis,
            "financial_summary": financial_summary,
            "affordability": affordability,
        }, avatar_state)

        state["budget_analysis"] = analysis
        state["financial_summary"] = financial_summary
        state["affordability"] = affordability
        state["agents_used"] = state.get("agents_used", []) + [self.name]
        state["events"] = state.get("events", []) + self.get_events()
        return state
