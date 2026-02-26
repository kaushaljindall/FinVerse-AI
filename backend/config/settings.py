"""
FinVerse AI — Configuration Settings
Centralized configuration using Pydantic BaseSettings with .env support.
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "FinVerse AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── LLM Configuration (Multi-Fallback) ──────────────
    GOOGLE_API_KEY: Optional[str] = None       # Primary: Gemini
    GROQ_API_KEY: Optional[str] = None         # Secondary: Groq (Llama 3)
    OPENAI_API_KEY: Optional[str] = None       # Tertiary: OpenAI

    GEMINI_MODEL: str = "gemini-2.0-flash"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OPENAI_MODEL: str = "gpt-4o-mini"

    # ── Web Search APIs ─────────────────────────────────
    TAVILY_API_KEY: Optional[str] = None       # Primary search
    SERPAPI_API_KEY: Optional[str] = None       # Fallback search

    # ── Vector Store ────────────────────────────────────
    FAISS_INDEX_DIR: str = "./data/faiss_index"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # ── Database ────────────────────────────────────────
    POSTGRES_URL: Optional[str] = None
    MONGODB_URI: Optional[str] = None
    REDIS_URL: Optional[str] = None

    # ── Authentication ──────────────────────────────────
    JWT_SECRET_KEY: str = "finverse-ai-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── Streaming ───────────────────────────────────────
    TRANSACTION_STREAM_INTERVAL: float = 3.0  # seconds between simulated txns

    # ── CORS ────────────────────────────────────────────
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
