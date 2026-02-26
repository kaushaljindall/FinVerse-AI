"""
FinVerse AI — Base Agent
Common interface for all specialized agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from backend.models.agent_response import AgentEvent, AvatarState
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all FinVerse agents."""

    def __init__(self, name: str, description: str, llm_provider=None):
        self.name = name
        self.description = description
        self.llm = llm_provider
        self.events: list[AgentEvent] = []

    def emit_event(self, event_type: str, content: Any, avatar_state: AvatarState = AvatarState.THINKING) -> AgentEvent:
        """Create and store an agent event for streaming to the frontend."""
        event = AgentEvent(
            type=event_type,
            agent=self.name,
            content=content,
            avatar_state=avatar_state,
        )
        self.events.append(event)
        return event

    async def think(self, prompt: str, system_prompt: str = "") -> str:
        """Use LLM to reason about a problem."""
        if self.llm is None:
            return "LLM not available"

        self.emit_event("thinking", {"message": f"{self.name} is reasoning..."}, AvatarState.THINKING)
        response, provider = await self.llm.generate(prompt, system_prompt)
        return response

    @abstractmethod
    async def execute(self, state: dict) -> dict:
        """
        Execute the agent's task.
        Args:
            state: Shared state dictionary from the orchestrator
        Returns:
            Updated state dictionary
        """
        pass

    def get_events(self) -> list[AgentEvent]:
        """Get all events emitted by this agent and clear the buffer."""
        events = self.events.copy()
        self.events = []
        return events
