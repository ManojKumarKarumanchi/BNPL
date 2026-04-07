"""EMI calculation utilities."""

import math
from typing import List, Dict, Any
import config


def calculate_emi(
    principal: float,
    annual_rate: float,
    months: int
) -> float:
    """
    Calculate EMI using standard formula.

    Args:
        principal: Loan amount
        annual_rate: Annual interest rate (percentage)
        months: Loan tenure in months

    Returns:
        Monthly EMI amount
    """
    if annual_rate == 0:
        # No cost EMI
        return round(principal / months, 2)

    # Convert annual rate to monthly
    monthly_rate = annual_rate / 12 / 100

    # EMI formula: P * r * (1+r)^n / ((1+r)^n - 1)
    emi = principal * monthly_rate * math.pow(1 + monthly_rate, months) / (
        math.pow(1 + monthly_rate, months) - 1
    )

    return round(emi, 2)


def generate_emi_plans(
    purchase_amount: float,
    credit_tier: str,
    credit_limit: float
) -> List[Dict[str, Any]]:
    """
    Generate EMI options based on credit tier.

    Args:
        purchase_amount: Purchase amount
        credit_tier: User's credit tier
        credit_limit: User's credit limit

    Returns:
        List of EMI options
    """
    tier_config = config.CREDIT_TIERS.get(credit_tier, {})
    emi_durations = tier_config.get("emi_durations", [])

    if not emi_durations or purchase_amount > credit_limit:
        return []

    emi_options = []

    for i, duration in enumerate(emi_durations, start=1):
        interest_rate = config.EMI_INTEREST_RATES.get(duration, 0)

        monthly_payment = calculate_emi(purchase_amount, interest_rate, duration)
        total_amount = monthly_payment * duration

        # Determine tag
        tag = None
        if interest_rate == 0:
            tag = "No Cost EMI"
        elif i == 2 and credit_tier == "regular":  # 6-month for regular users
            tag = "Best Value"
        elif duration == 9 and credit_tier == "power":
            tag = "VIP Rate"

        emi_options.append({
            "id": i,
            "duration": duration,
            "monthly_payment": monthly_payment,
            "tag": tag,
            "total_amount": round(total_amount, 2),
            "interest_rate": interest_rate
        })

    return emi_options
