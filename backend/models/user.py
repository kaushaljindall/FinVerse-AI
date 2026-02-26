"""
FinVerse AI — User Profile & Budget Models
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BudgetCategory(BaseModel):
    """Budget allocation for a spending category."""
    category: str
    limit: float
    spent: float = 0.0

    @property
    def remaining(self) -> float:
        return max(0, self.limit - self.spent)

    @property
    def utilization(self) -> float:
        if self.limit == 0:
            return 0.0
        return min(1.0, self.spent / self.limit)


class UserProfile(BaseModel):
    """User financial profile for agent context."""
    user_id: str = "default_user"
    name: str = "User"
    monthly_income: float = 80000.0
    total_balance: float = 250000.0
    savings_goal: float = 20000.0
    risk_tolerance: str = "moderate"  # conservative, moderate, aggressive

    budgets: list[BudgetCategory] = Field(default_factory=lambda: [
        BudgetCategory(category="food", limit=15000, spent=0),
        BudgetCategory(category="transport", limit=5000, spent=0),
        BudgetCategory(category="shopping", limit=10000, spent=0),
        BudgetCategory(category="entertainment", limit=5000, spent=0),
        BudgetCategory(category="utilities", limit=8000, spent=0),
        BudgetCategory(category="healthcare", limit=5000, spent=0),
        BudgetCategory(category="education", limit=3000, spent=0),
        BudgetCategory(category="rent", limit=20000, spent=0),
        BudgetCategory(category="subscription", limit=2000, spent=0),
    ])

    monthly_transactions: list = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def total_budget(self) -> float:
        return sum(b.limit for b in self.budgets)

    @property
    def total_spent(self) -> float:
        return sum(b.spent for b in self.budgets)

    @property
    def discretionary_balance(self) -> float:
        return self.monthly_income - self.total_spent - self.savings_goal

    def get_budget(self, category: str) -> Optional[BudgetCategory]:
        for b in self.budgets:
            if b.category == category:
                return b
        return None

    def update_spending(self, category: str, amount: float):
        budget = self.get_budget(category)
        if budget:
            budget.spent += amount
