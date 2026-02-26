"""
FinVerse AI — Explanation Agent
Converts agent reasoning into structured, clean summaries.
Never exposes internal chain-of-thought.
"""

import logging
from backend.agents.base_agent import BaseAgent
from backend.models.agent_response import AvatarState

logger = logging.getLogger(__name__)


class ExplanationAgent(BaseAgent):
    """
    Agent 6: Explanation Agent
    - Synthesizes outputs from all other agents
    - Generates clean, structured final responses
    - Provides concise justification
    - Never exposes internal chain-of-thought
    """

    def __init__(self, llm_provider=None):
        super().__init__(
            name="explanation_agent",
            description="Synthesizes multi-agent outputs into clear, structured explanations",
            llm_provider=llm_provider,
        )

    async def execute(self, state: dict) -> dict:
        """Synthesize all agent outputs into a final, clean response."""
        query = state.get("query", "")

        self.emit_event("thinking", {
            "message": "Synthesizing insights from all agents into a clear response..."
        }, AvatarState.THINKING)

        # Gather all agent outputs
        sections = []

        if state.get("transaction_analysis"):
            sections.append(f"Transaction Intelligence:\n{state['transaction_analysis']}")

        if state.get("budget_analysis"):
            sections.append(f"Budget Analysis:\n{state['budget_analysis']}")

        if state.get("compliance_analysis"):
            sections.append(f"Compliance Status:\n{state['compliance_analysis']}")

        if state.get("shopping_results"):
            shop = state["shopping_results"]
            sections.append(f"Shopping Intelligence:\n{shop.get('recommendation', 'No recommendation available')}")

        if state.get("rag_analysis"):
            sections.append(f"Document Research:\n{state['rag_analysis']}")

        if not sections:
            # No prior agent analysis — this agent handles the query directly
            system_prompt = """You are FinVerse AI, a Financial Operating System.
Answer the user's financial question clearly and helpfully.
Be concise, structured, and actionable.
If this is a general financial question, provide expert-level advice.
If you need specific data you don't have, say so."""

            response = await self.think(query, system_prompt)
        else:
            # Synthesize all agent outputs
            combined = "\n\n---\n\n".join(sections)
            citations = state.get("citations", [])

            system_prompt = """You are the Explanation Agent for FinVerse AI.
Your role is to create the FINAL response the user will see.

Rules:
1. Synthesize all agent analyses into ONE clear, structured response
2. Use headers, bullet points, and formatting for clarity
3. NEVER expose internal reasoning or chain-of-thought
4. Provide a clear ACTION-ORIENTED conclusion
5. Include relevant warnings and recommendations
6. If citations exist, include them
7. Be concise — busy professionals read this
8. The tone should be professional but friendly"""

            prompt = f"""User's Original Query: {query}

Agent Analyses:
{combined}

{f'Document Citations: {", ".join(citations)}' if citations else ''}

Agents Used: {", ".join(state.get("agents_used", []))}

Create a polished, final response. Structure it clearly with sections."""

            response = await self.think(prompt, system_prompt)

        self.emit_event("result", {
            "agent": self.name,
            "type": "final_response",
            "response": response,
        }, AvatarState.RECOMMENDING)

        state["final_response"] = response
        state["agents_used"] = state.get("agents_used", []) + [self.name]
        state["events"] = state.get("events", []) + self.get_events()
        return state
