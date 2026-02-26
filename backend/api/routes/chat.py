"""
FinVerse AI — Chat API Route
Handles user queries via the multi-agent orchestrator.
Supports both REST and streaming (SSE) modes.
"""

import json
import asyncio
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from backend.agents.orchestrator import AgentOrchestrator
from backend.models.user import UserProfile
from backend.models.agent_response import AgentEvent
from backend.streaming.transaction_simulator import generate_transaction_batch

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# Global orchestrator (initialized in main.py)
_orchestrator: Optional[AgentOrchestrator] = None
_user_profile: Optional[UserProfile] = None
_transactions: list = []


def init_chat(orchestrator: AgentOrchestrator):
    """Initialize the chat route with the orchestrator."""
    global _orchestrator, _user_profile, _transactions
    _orchestrator = orchestrator
    _user_profile = UserProfile()
    _transactions = generate_transaction_batch(30)

    # Update user profile with transaction spending
    for txn in _transactions:
        if not txn.get("is_credit", False):
            _user_profile.update_spending(txn.get("category", "other"), txn.get("amount", 0))


class ChatRequest(BaseModel):
    query: str
    stream: bool = True


class ChatResponse(BaseModel):
    response: str
    agents_used: list[str] = []
    citations: list[str] = []
    processing_time: float = 0
    avatar_state: str = "idle"


@router.post("/query")
async def chat_query(request: ChatRequest):
    """Process a chat query through the multi-agent system."""
    if not _orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    if request.stream:
        return StreamingResponse(
            _stream_response(request.query),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )
    else:
        # Non-streaming mode
        result = await _orchestrator.process_query(
            query=request.query,
            user_profile=_user_profile,
            transactions=_transactions,
        )
        return ChatResponse(
            response=result.response,
            agents_used=result.agents_used,
            citations=result.citations,
            processing_time=result.processing_time,
            avatar_state=result.avatar_state.value,
        )


async def _stream_response(query: str):
    """Stream agent events as SSE."""
    event_queue = asyncio.Queue()

    async def event_callback(event: AgentEvent):
        await event_queue.put(event)

    # Start processing in background
    async def process():
        try:
            result = await _orchestrator.process_query(
                query=query,
                user_profile=_user_profile,
                transactions=_transactions,
                event_callback=event_callback,
            )
            # Send final response
            await event_queue.put(AgentEvent(
                type="final",
                agent="orchestrator",
                content={
                    "response": result.response,
                    "agents_used": result.agents_used,
                    "citations": result.citations,
                    "processing_time": result.processing_time,
                },
                avatar_state=result.avatar_state,
            ))
            await event_queue.put(None)  # Signal end
        except Exception as e:
            logger.error(f"Processing error: {e}")
            await event_queue.put(AgentEvent(
                type="error",
                agent="orchestrator",
                content={"error": str(e)},
            ))
            await event_queue.put(None)

    asyncio.create_task(process())

    # Yield events as SSE
    while True:
        event = await event_queue.get()
        if event is None:
            break

        event_data = {
            "type": event.type,
            "agent": event.agent,
            "content": event.content,
            "avatar_state": event.avatar_state.value if hasattr(event.avatar_state, 'value') else str(event.avatar_state),
            "timestamp": event.timestamp.isoformat(),
        }
        yield f"data: {json.dumps(event_data)}\n\n"

    yield "data: [DONE]\n\n"


@router.get("/health")
async def chat_health():
    """Check if the chat system is healthy."""
    return {
        "status": "ok",
        "orchestrator": _orchestrator is not None,
        "transactions_loaded": len(_transactions),
        "user_profile_loaded": _user_profile is not None,
    }
