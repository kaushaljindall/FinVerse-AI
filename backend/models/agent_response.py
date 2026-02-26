"""
FinVerse AI — Agent Response & Event Models
These models define the streaming event protocol between backend and frontend.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class AvatarState(str, Enum):
    """3D Avatar animation states — driven by agent tool calls."""
    IDLE = "idle"
    THINKING = "thinking"
    SEARCHING = "searching"
    ANALYZING = "analyzing"
    ALERT = "alert"
    RECOMMENDING = "recommending"


class ToolCall(BaseModel):
    """A visible tool call made by an agent."""
    tool_name: str
    tool_input: dict = {}
    tool_output: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentEvent(BaseModel):
    """
    A single streaming event from the agent system.
    Sent via WebSocket/SSE to the frontend.
    """
    type: str  # "plan", "search", "tool_call", "result", "thinking", "error", "avatar_state", "final"
    agent: Optional[str] = None  # Which agent generated this event
    content: Any = None  # Event payload
    avatar_state: AvatarState = AvatarState.IDLE
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "type": "search",
                "agent": "shopping_agent",
                "content": {"query": "iPhone 15 price Amazon", "status": "executing"},
                "avatar_state": "searching",
            }
        }


class AgentResponse(BaseModel):
    """Final aggregated response from the agent orchestration."""
    query: str
    response: str
    agents_used: list[str] = []
    tool_calls: list[ToolCall] = []
    events: list[AgentEvent] = []
    citations: list[str] = []
    avatar_state: AvatarState = AvatarState.IDLE
    processing_time: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
