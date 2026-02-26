"""
FinVerse AI — Budget Calculator Tool
Computes budget health, discretionary balance, and purchase affordability.
"""

from backend.models.user import UserProfile
from typing import Optional


class BudgetCalculator:
    """Financial health calculator for budget-aware recommendations."""

    def check_purchase_affordability(
        self,
        user: UserProfile,
        amount: float,
        category: str
    ) -> dict:
        """
        Check if a purchase is affordable and safe.
        Returns structured affordability analysis.
        """
        budget = user.get_budget(category)
        discretionary = user.discretionary_balance

        result = {
            "affordable": discretionary >= amount,
            "amount": amount,
            "category": category,
            "discretionary_balance": discretionary,
            "remaining_after": discretionary - amount,
            "budget_status": None,
            "warnings": [],
            "recommendation": "",
        }

        # Check category budget
        if budget:
            result["budget_status"] = {
                "limit": budget.limit,
                "spent": budget.spent,
                "remaining": budget.remaining,
                "utilization": round(budget.utilization * 100, 1),
                "would_exceed": budget.spent + amount > budget.limit,
            }

            if budget.spent + amount > budget.limit:
                excess = (budget.spent + amount) - budget.limit
                result["warnings"].append(
                    f"This purchase exceeds your {category} budget by ₹{excess:,.0f}"
                )

        # Check overall affordability
        if amount > discretionary:
            excess = amount - discretionary
            result["warnings"].append(
                f"This purchase exceeds your safe spending threshold by ₹{excess:,.0f}"
            )
            result["recommendation"] = "⚠️ Consider postponing this purchase or adjusting your budget."
        elif amount > discretionary * 0.5:
            result["warnings"].append(
                "This purchase would use more than 50% of your remaining discretionary balance."
            )
            result["recommendation"] = "⚡ Affordable, but be cautious with large purchases this month."
        else:
            result["recommendation"] = "✅ This purchase is within your comfortable spending range."

        # Check savings impact
        if user.total_balance - amount < user.savings_goal * 3:
            result["warnings"].append(
                "Your balance after this purchase would be less than 3x your savings goal."
            )

        return result

    def get_financial_summary(self, user: UserProfile) -> dict:
        """Get overall financial health summary."""
        total_spent = user.total_spent
        income = user.monthly_income

        return {
            "monthly_income": income,
            "total_balance": user.total_balance,
            "total_spent": total_spent,
            "discretionary_balance": user.discretionary_balance,
            "savings_goal": user.savings_goal,
            "spending_ratio": round((total_spent / income * 100) if income > 0 else 0, 1),
            "budgets": [
                {
                    "category": b.category,
                    "limit": b.limit,
                    "spent": b.spent,
                    "remaining": b.remaining,
                    "utilization_pct": round(b.utilization * 100, 1),
                }
                for b in user.budgets
            ],
            "health_score": self._calculate_health_score(user),
        }

    def _calculate_health_score(self, user: UserProfile) -> dict:
        """Calculate a financial health score (0-100)."""
        score = 100

        # Penalize for overspending
        spending_ratio = user.total_spent / user.monthly_income if user.monthly_income > 0 else 1
        if spending_ratio > 0.8:
            score -= 30
        elif spending_ratio > 0.6:
            score -= 15

        # Penalize for low balance
        if user.total_balance < user.savings_goal * 2:
            score -= 20
        elif user.total_balance < user.savings_goal * 5:
            score -= 10

        # Penalize for budget overruns
        overrun_count = sum(1 for b in user.budgets if b.utilization > 1.0)
        score -= overrun_count * 5

        score = max(0, min(100, score))

        if score >= 80:
            label = "Excellent"
            color = "#10b981"
        elif score >= 60:
            label = "Good"
            color = "#f59e0b"
        elif score >= 40:
            label = "Needs Attention"
            color = "#f97316"
        else:
            label = "Critical"
            color = "#ef4444"

        return {"score": score, "label": label, "color": color}
