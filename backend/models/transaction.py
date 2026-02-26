"""
FinVerse AI — Transaction Data Models
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class TransactionCategory(str, Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    RENT = "rent"
    SALARY = "salary"
    INVESTMENT = "investment"
    TRANSFER = "transfer"
    SUBSCRIPTION = "subscription"
    TRAVEL = "travel"
    OTHER = "other"


class Transaction(BaseModel):
    """A single financial transaction."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    amount: float
    category: TransactionCategory
    merchant: str
    description: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_credit: bool = False  # True = income, False = expense
    location: Optional[str] = None
    is_flagged: bool = False
    fraud_score: float = 0.0
    tags: list[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 2499.00,
                "category": "shopping",
                "merchant": "Amazon",
                "description": "Electronics purchase",
                "is_credit": False,
                "location": "Online",
            }
        }
