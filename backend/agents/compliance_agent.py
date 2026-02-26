"""
FinVerse AI — Compliance Validator Agent
Validates responses against compliance rules, checks fraud risk.
"""

import logging
from backend.agents.base_agent import BaseAgent
from backend.models.agent_response import AvatarState
from backend.tools.compliance_rules import ComplianceEngine

logger = logging.getLogger(__name__)


class ComplianceAgent(BaseAgent):
    """
    Agent 3: Compliance Validator
    - Checks responses against compliance rules
    - Validates fraud risk for transactions
    - Prevents unsafe outputs
    - Generates audit trails
    """

    def __init__(self, llm_provider=None):
        super().__init__(
            name="compliance_agent",
            description="Validates transactions and responses against financial regulations",
            llm_provider=llm_provider,
        )
        self.engine = ComplianceEngine()

    async def execute(self, state: dict) -> dict:
        """Run compliance checks on the current state."""
        query = state.get("query", "")
        transactions = state.get("transactions", [])

        self.emit_event("thinking", {
            "message": "Running compliance and fraud risk checks..."
        }, AvatarState.ANALYZING)

        # Validate transactions
        compliance_results = []
        for txn in transactions[-5:]:  # Check recent transactions
            result = self.engine.validate_transaction(txn if isinstance(txn, dict) else txn.dict())
            compliance_results.append(result)

            if not result["compliant"]:
                self.emit_event("tool_call", {
                    "tool": "compliance_engine",
                    "action": "transaction_validation",
                    "violations": result["violations"],
                    "risk_level": result["risk_level"],
                }, AvatarState.ALERT)

        # Check any generated recommendations
        prior_analysis = state.get("transaction_analysis", "") + " " + state.get("budget_analysis", "")
        if prior_analysis.strip():
            rec_check = self.engine.validate_recommendation(prior_analysis)
            if not rec_check["safe"]:
                self.emit_event("tool_call", {
                    "tool": "compliance_engine",
                    "action": "recommendation_validation",
                    "violations": rec_check["violations"],
                }, AvatarState.ALERT)

        # LLM compliance summary
        system_prompt = """You are the Compliance Validator Agent for FinVerse AI.
Your role is to:
1. Summarize compliance check results
2. Highlight any violations or risks
3. Recommend corrective actions
4. Ensure all advice is regulation-safe

Be precise and authoritative. Use formal language."""

        violations_summary = []
        for r in compliance_results:
            if not r["compliant"]:
                for v in r["violations"]:
                    violations_summary.append(f"- [{v['rule_id']}] {v['message']} (Severity: {v['severity']})")

        prompt = f"""Query: {query}

Compliance Check Results:
- Transactions checked: {len(compliance_results)}
- Violations found: {sum(1 for r in compliance_results if not r['compliant'])}

{chr(10).join(violations_summary) if violations_summary else 'No violations detected. All transactions are compliant.'}

Provide a compliance summary."""

        analysis = await self.think(prompt, system_prompt)

        has_violations = any(not r["compliant"] for r in compliance_results)

        self.emit_event("result", {
            "agent": self.name,
            "analysis": analysis,
            "compliant": not has_violations,
            "violations_count": sum(1 for r in compliance_results if not r["compliant"]),
        }, AvatarState.ALERT if has_violations else AvatarState.RECOMMENDING)

        state["compliance_analysis"] = analysis
        state["compliance_results"] = compliance_results
        state["agents_used"] = state.get("agents_used", []) + [self.name]
        state["events"] = state.get("events", []) + self.get_events()
        return state
