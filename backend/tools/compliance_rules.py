"""
FinVerse AI — Compliance Rules Engine
Validates transactions and recommendations against financial regulations.
"""

from typing import Optional
from datetime import datetime


# Compliance rule definitions
COMPLIANCE_RULES = [
    {
        "id": "AML_001",
        "name": "Anti-Money Laundering - Large Transaction",
        "description": "Flag transactions exceeding ₹10,00,000 as per RBI AML guidelines",
        "threshold": 1000000,
        "type": "transaction_amount",
        "severity": "high",
    },
    {
        "id": "AML_002",
        "name": "Anti-Money Laundering - Suspicious Pattern",
        "description": "Flag multiple transactions just below reporting threshold",
        "threshold": 900000,
        "type": "structuring_detection",
        "severity": "high",
    },
    {
        "id": "FRAUD_001",
        "name": "Unusual Transaction Time",
        "description": "Flag transactions between 1 AM - 5 AM local time",
        "type": "time_anomaly",
        "severity": "medium",
    },
    {
        "id": "FRAUD_002",
        "name": "High-Frequency Transactions",
        "description": "Flag more than 10 transactions in 1 hour",
        "threshold": 10,
        "type": "frequency_anomaly",
        "severity": "medium",
    },
    {
        "id": "BUDGET_001",
        "name": "Budget Overrun Prevention",
        "description": "Warn when category spending exceeds 90% of budget",
        "threshold": 0.9,
        "type": "budget_check",
        "severity": "low",
    },
    {
        "id": "RISK_001",
        "name": "High-Risk Merchant Category",
        "description": "Flag transactions from gambling, crypto, or high-risk merchants",
        "type": "merchant_risk",
        "severity": "medium",
        "high_risk_categories": ["gambling", "crypto", "forex"],
    },
]


class ComplianceEngine:
    """Rule-based compliance validator for financial transactions."""

    def __init__(self):
        self.rules = COMPLIANCE_RULES

    def validate_transaction(self, transaction: dict) -> dict:
        """
        Validate a transaction against all compliance rules.
        Returns violations and risk assessment.
        """
        violations = []
        amount = transaction.get("amount", 0)

        # AML_001: Large transaction check
        if amount >= 1000000:
            violations.append({
                "rule_id": "AML_001",
                "severity": "high",
                "message": f"Transaction of ₹{amount:,.0f} exceeds AML reporting threshold (₹10,00,000)",
                "action": "Report to Financial Intelligence Unit",
            })

        # FRAUD_001: Unusual time check
        timestamp = transaction.get("timestamp")
        if timestamp:
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            hour = timestamp.hour
            if 1 <= hour <= 5:
                violations.append({
                    "rule_id": "FRAUD_001",
                    "severity": "medium",
                    "message": f"Transaction at unusual hour ({hour}:00). Potential unauthorized access.",
                    "action": "Verify with account holder",
                })

        # RISK_001: High-risk merchant check
        category = transaction.get("category", "").lower()
        merchant = transaction.get("merchant", "").lower()
        high_risk_terms = ["gambling", "casino", "crypto", "forex", "betting"]
        if any(term in category or term in merchant for term in high_risk_terms):
            violations.append({
                "rule_id": "RISK_001",
                "severity": "medium",
                "message": f"Transaction with high-risk merchant/category: {merchant}",
                "action": "Enhanced due diligence required",
            })

        # Calculate overall risk
        risk_score = self._calculate_risk_score(violations)

        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "risk_score": risk_score,
            "risk_level": "high" if risk_score > 70 else "medium" if risk_score > 30 else "low",
            "rules_checked": len(self.rules),
        }

    def validate_recommendation(self, recommendation: str) -> dict:
        """
        Validate that an AI recommendation doesn't violate compliance rules.
        Ensures we never recommend illegal or unsafe financial actions.
        """
        unsafe_terms = [
            "guaranteed returns", "no risk", "insider", "tax evasion",
            "hide income", "unregulated", "ponzi", "pyramid",
        ]

        violations = []
        rec_lower = recommendation.lower()

        for term in unsafe_terms:
            if term in rec_lower:
                violations.append({
                    "rule_id": "COMPLIANCE_OUTPUT",
                    "severity": "high",
                    "message": f"Recommendation contains unsafe term: '{term}'",
                    "action": "Rewrite recommendation to remove unsafe language",
                })

        return {
            "safe": len(violations) == 0,
            "violations": violations,
        }

    def _calculate_risk_score(self, violations: list) -> float:
        """Calculate risk score based on violations."""
        if not violations:
            return 0.0

        severity_weights = {"high": 40, "medium": 20, "low": 10}
        total = sum(severity_weights.get(v["severity"], 10) for v in violations)
        return min(100.0, total)
