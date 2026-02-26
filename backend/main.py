"""
FinVerse AI — FastAPI Main Entry Point
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.config.settings import settings
from backend.agents.orchestrator import AgentOrchestrator
from backend.api.routes.chat import router as chat_router, init_chat
from backend.api.routes.transactions import router as txn_router, init_transactions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    logger.info("🚀 Starting FinVerse AI...")
    logger.info(f"   App: {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"   Debug: {settings.DEBUG}")

    # Initialize orchestrator
    orchestrator = AgentOrchestrator(settings)
    init_chat(orchestrator)
    init_transactions()

    logger.info("✅ FinVerse AI is ready!")
    logger.info(f"   API Docs: http://localhost:{settings.PORT}/docs")

    yield

    logger.info("👋 Shutting down FinVerse AI...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise-Grade Agentic Financial Operating System with Embodied AI",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(chat_router)
app.include_router(txn_router)


@app.get("/")
async def root():
    """Health check."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "agents": [
            "Transaction Intelligence",
            "Budget Guardian",
            "Compliance Validator",
            "Shopping Intelligence",
            "RAG Retrieval",
            "Explanation",
        ]
    }


@app.get("/api/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "llm_providers": {
            "gemini": bool(settings.GOOGLE_API_KEY),
            "groq": bool(settings.GROQ_API_KEY),
            "openai": bool(settings.OPENAI_API_KEY),
        },
        "search_providers": {
            "tavily": bool(settings.TAVILY_API_KEY),
            "serpapi": bool(settings.SERPAPI_API_KEY),
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
