"""
FinVerse AI — Transaction API Routes
"""

import logging
from fastapi import APIRouter
from backend.streaming.transaction_simulator import generate_transaction, generate_transaction_batch

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

# In-memory transaction store (would be database in production)
_transactions: list = []


def init_transactions():
    """Initialize with seed data."""
    global _transactions
    _transactions = generate_transaction_batch(30)


@router.get("/")
async def get_transactions(limit: int = 50):
    """Get recent transactions."""
    return {
        "transactions": _transactions[-limit:],
        "total": len(_transactions),
    }


@router.post("/generate")
async def generate_new_transaction():
    """Generate a new random transaction (for demo)."""
    txn = generate_transaction()
    _transactions.append(txn)
    return {"transaction": txn, "total": len(_transactions)}


@router.get("/summary")
async def get_transaction_summary():
    """Get spending summary."""
    categories = {}
    total_spent = 0
    total_income = 0

    for txn in _transactions:
        amount = txn.get("amount", 0)
        cat = txn.get("category", "other")

        if txn.get("is_credit", False):
            total_income += amount
        else:
            total_spent += amount
            categories[cat] = categories.get(cat, 0) + amount

    return {
        "total_spent": round(total_spent, 2),
        "total_income": round(total_income, 2),
        "net": round(total_income - total_spent, 2),
        "categories": {k: round(v, 2) for k, v in sorted(categories.items(), key=lambda x: -x[1])},
        "transaction_count": len(_transactions),
        "flagged_count": sum(1 for t in _transactions if t.get("is_flagged", False)),
    }
