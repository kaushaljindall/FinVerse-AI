"""
FinVerse AI — Transaction Simulator
Generates realistic transaction data for demo/development.
"""

import random
import uuid
from datetime import datetime, timedelta
from backend.models.transaction import Transaction, TransactionCategory


# Merchant data organized by category
MERCHANTS = {
    TransactionCategory.FOOD: [
        ("Swiggy", 150, 800), ("Zomato", 200, 1200), ("BigBasket", 500, 3000),
        ("Dominos", 300, 900), ("Starbucks", 250, 600), ("Haldiram's", 100, 500),
    ],
    TransactionCategory.TRANSPORT: [
        ("Uber", 100, 800), ("Ola", 80, 600), ("Metro Card", 200, 500),
        ("Indian Oil", 500, 5000), ("IRCTC", 300, 3000),
    ],
    TransactionCategory.SHOPPING: [
        ("Amazon", 500, 25000), ("Flipkart", 300, 20000), ("Myntra", 400, 5000),
        ("Nike Store", 2000, 15000), ("Croma", 1000, 50000),
    ],
    TransactionCategory.ENTERTAINMENT: [
        ("Netflix", 149, 649), ("Spotify", 119, 119), ("BookMyShow", 200, 1500),
        ("Disney+ Hotstar", 299, 1499), ("Steam", 200, 3000),
    ],
    TransactionCategory.UTILITIES: [
        ("Jio Recharge", 239, 999), ("Electricity Bill", 800, 5000),
        ("Water Bill", 200, 800), ("Gas Bill", 300, 1200), ("Broadband", 600, 1500),
    ],
    TransactionCategory.HEALTHCARE: [
        ("Apollo Pharmacy", 200, 2000), ("1mg", 100, 1500),
        ("Dr. Consultation", 500, 2000), ("Lab Tests", 300, 5000),
    ],
    TransactionCategory.SUBSCRIPTION: [
        ("Netflix", 149, 649), ("Spotify", 119, 119), ("YouTube Premium", 129, 129),
        ("Amazon Prime", 179, 179), ("Coursera", 2499, 4999),
    ],
    TransactionCategory.RENT: [
        ("House Rent", 15000, 25000),
    ],
    TransactionCategory.SALARY: [
        ("Employer - TCS", 50000, 150000), ("Employer - Infosys", 40000, 120000),
        ("Freelance Payment", 5000, 50000),
    ],
}

LOCATIONS = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
    "Pune", "Kolkata", "Online", "Noida", "Gurgaon",
]


def generate_transaction(bias_category: TransactionCategory = None) -> dict:
    """Generate a single realistic random transaction."""
    # Pick category (with optional bias)
    if bias_category:
        category = bias_category
    else:
        # Weight categories by frequency
        categories = list(MERCHANTS.keys())
        weights = [25, 15, 15, 10, 10, 5, 5, 3, 12]  # Approximate real distribution
        category = random.choices(categories, weights=weights[:len(categories)], k=1)[0]

    # Pick merchant
    merchants = MERCHANTS.get(category, [("Unknown", 100, 1000)])
    merchant_name, min_amount, max_amount = random.choice(merchants)

    # Generate amount
    amount = round(random.uniform(min_amount, max_amount), 2)

    # Determine if credit (income)
    is_credit = category in [TransactionCategory.SALARY, TransactionCategory.INVESTMENT]

    # Random time within last 30 days
    hours_ago = random.randint(0, 720)
    timestamp = datetime.utcnow() - timedelta(hours=hours_ago)

    # Small chance of anomaly (for fraud detection demo)
    is_anomaly = random.random() < 0.05  # 5% chance
    if is_anomaly:
        amount *= random.uniform(3, 10)  # Spike the amount
        amount = round(amount, 2)

    return {
        "id": str(uuid.uuid4()),
        "amount": amount,
        "category": category.value,
        "merchant": merchant_name,
        "description": f"{'Received from' if is_credit else 'Payment to'} {merchant_name}",
        "timestamp": timestamp.isoformat(),
        "is_credit": is_credit,
        "location": random.choice(LOCATIONS),
        "is_flagged": is_anomaly,
        "fraud_score": round(random.uniform(0.5, 0.95), 2) if is_anomaly else round(random.uniform(0, 0.2), 2),
        "tags": ["anomaly"] if is_anomaly else [],
    }


def generate_transaction_batch(count: int = 30) -> list[dict]:
    """Generate a batch of transactions simulating a month of activity."""
    transactions = []

    # Always include at least one salary
    transactions.append(generate_transaction(TransactionCategory.SALARY))

    # Generate rest
    for _ in range(count - 1):
        transactions.append(generate_transaction())

    # Sort by timestamp
    transactions.sort(key=lambda x: x["timestamp"])
    return transactions
