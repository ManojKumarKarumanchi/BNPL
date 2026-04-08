"""
Persona configurations for GrabOn BNPL synthetic data generation.
Matches frontend personas exactly: frontend/src/data/mockData.js
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List

# Real GrabOn merchants (from frontend/src/data/realGrabOnDeals.js)
GRABON_MERCHANTS = [
    {"id": "MRCH_AMAZON", "name": "Amazon", "deal_count": 847, "avg_discount": 75},
    {"id": "MRCH_FLIPKART", "name": "Flipkart", "deal_count": 623, "avg_discount": 70},
    {"id": "MRCH_MYNTRA", "name": "Myntra", "deal_count": 512, "avg_discount": 55},
    {"id": "MRCH_NYKAA", "name": "Nykaa", "deal_count": 389, "avg_discount": 40},
    {"id": "MRCH_MAKEMYTRIP", "name": "MakeMyTrip", "deal_count": 234, "avg_discount": 25},
    {"id": "MRCH_SWIGGY", "name": "Swiggy", "deal_count": 156, "avg_discount": 30},
]

# Real GrabOn categories (from frontend business data)
GRABON_CATEGORIES = [
    {"name": "Electronics", "weight": 0.10},
    {"name": "Fashion", "weight": 0.24},  # Highest category
    {"name": "Beauty", "weight": 0.08},
    {"name": "Travel", "weight": 0.17},
    {"name": "Food", "weight": 0.16},
    {"name": "Health", "weight": 0.08},
]

# Payment modes
PAYMENT_MODES = ["upi", "card", "netbanking"]

# Coupon codes (realistic GrabOn patterns)
COUPON_CODES = [
    "SAMSUNG50", "GRABON2249", "GRABON1499", "PUMA60", "NYKAA40",
    "GRABON500", "FLASH50", "WEEKEND25", "APP30", "FIRST100"
]


class PersonaConfig:
    """Base configuration for a user persona."""

    def __init__(
        self,
        user_id: str,
        name: str,
        email: str,
        total_purchases: int,
        avg_order_value: float,
        return_rate: float,
        coupon_redemption_rate: float,
        member_since: datetime,
        category_preferences: Dict[str, float],
        merchant_preferences: Dict[str, float],
        credit_tier: str
    ):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.total_purchases = total_purchases
        self.avg_order_value = avg_order_value
        self.return_rate = return_rate
        self.coupon_redemption_rate = coupon_redemption_rate
        self.member_since = member_since
        self.category_preferences = category_preferences
        self.merchant_preferences = merchant_preferences
        self.credit_tier = credit_tier


# Persona 1: Brand New User (0 transactions)
RAJESH_CONFIG = PersonaConfig(
    user_id="USR_RAJESH",
    name="Rajesh Kumar",
    email="rajesh.kumar@example.com",
    total_purchases=0,
    avg_order_value=0,
    return_rate=0.0,
    coupon_redemption_rate=0.0,
    member_since=datetime(2026, 4, 1),  # 6 days ago (fraud check trigger)
    category_preferences={},
    merchant_preferences={},
    credit_tier="new_user"
)

# Persona 2: Risky User (Few transactions, high returns)
PRIYA_CONFIG = PersonaConfig(
    user_id="USR_PRIYA",
    name="Priya Sharma",
    email="priya.sharma@example.com",
    total_purchases=8,
    avg_order_value=950,
    return_rate=0.18,  # 18% return rate → Rejection trigger
    coupon_redemption_rate=0.45,  # Low coupon redemption
    member_since=datetime(2025, 12, 10),
    category_preferences={
        "Fashion": 0.60,  # Heavy fashion buyer (impulse purchases)
        "Beauty": 0.30,
        "Electronics": 0.10
    },
    merchant_preferences={
        "MRCH_MYNTRA": 0.50,
        "MRCH_NYKAA": 0.30,
        "MRCH_AMAZON": 0.20
    },
    credit_tier="risky"
)

# Persona 3: Growing User (Moderate history)
AMIT_CONFIG = PersonaConfig(
    user_id="USR_AMIT",
    name="Amit Patel",
    email="amit.patel@example.com",
    total_purchases=25,
    avg_order_value=1850,
    return_rate=0.04,  # 4% return rate (acceptable)
    coupon_redemption_rate=0.78,  # Good coupon usage
    member_since=datetime(2025, 12, 1),
    category_preferences={
        "Electronics": 0.35,
        "Fashion": 0.25,
        "Food": 0.20,
        "Health": 0.20
    },
    merchant_preferences={
        "MRCH_AMAZON": 0.45,
        "MRCH_FLIPKART": 0.30,
        "MRCH_SWIGGY": 0.25
    },
    credit_tier="growing"
)

# Persona 4: Regular User (Good history)
SNEHA_CONFIG = PersonaConfig(
    user_id="USR_SNEHA",
    name="Sneha Reddy",
    email="sneha.reddy@example.com",
    total_purchases=48,
    avg_order_value=2850,
    return_rate=0.02,  # 2% return rate (excellent)
    coupon_redemption_rate=0.92,  # High coupon redemption
    member_since=datetime(2024, 8, 15),  # ~8 months tenure
    category_preferences={
        "Electronics": 0.30,
        "Fashion": 0.25,
        "Beauty": 0.20,
        "Health": 0.15,
        "Food": 0.10
    },
    merchant_preferences={
        "MRCH_AMAZON": 0.35,
        "MRCH_FLIPKART": 0.30,
        "MRCH_NYKAA": 0.20,
        "MRCH_MYNTRA": 0.15
    },
    credit_tier="regular"
)

# Persona 5: Power User (VIP status)
VIKRAM_CONFIG = PersonaConfig(
    user_id="USR_VIKRAM",
    name="Vikram Singh",
    email="vikram.singh@example.com",
    total_purchases=237,
    avg_order_value=4200,
    return_rate=0.0,  # 0% returns (perfect record)
    coupon_redemption_rate=0.98,  # 98% coupon redemption (VIP benefit)
    member_since=datetime(2024, 10, 15),  # ~18 months tenure
    category_preferences={
        "Electronics": 0.25,
        "Travel": 0.25,
        "Fashion": 0.20,
        "Beauty": 0.15,
        "Health": 0.10,
        "Food": 0.05
    },
    merchant_preferences={
        "MRCH_AMAZON": 0.35,
        "MRCH_FLIPKART": 0.25,
        "MRCH_MAKEMYTRIP": 0.20,
        "MRCH_MYNTRA": 0.10,
        "MRCH_NYKAA": 0.10
    },
    credit_tier="power"
)

# All personas for iteration
ALL_PERSONAS = [
    RAJESH_CONFIG,
    PRIYA_CONFIG,
    AMIT_CONFIG,
    SNEHA_CONFIG,
    VIKRAM_CONFIG
]

# Credit tier mapping
CREDIT_TIER_MAPPING = {
    "new_user": {"credit_limit": 0, "emi_options": 0},
    "risky": {"credit_limit": 0, "emi_options": 0},
    "growing": {"credit_limit": 15000, "emi_options": 2},
    "regular": {"credit_limit": 25000, "emi_options": 3},
    "power": {"credit_limit": 50000, "emi_options": 4}  # Includes 12-month option
}

# Database configuration
import os
from pathlib import Path

DB_PATH = os.getenv(
    "DATABASE_PATH",
    str(Path(__file__).parent / "output" / "grabon_bnpl.db")
)
