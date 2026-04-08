"""EMI calculation utilities with precision validation."""

import math
from typing import List, Dict, Any
import logging
import config

logger = logging.getLogger(__name__)


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


def calculate_emi_precise(
    principal: float,
    annual_rate: float,
    months: int
) -> Dict[str, float]:
    """
    Calculate EMI with high precision and validation.

    Provides transparent calculation showing:
    - Exact EMI before rounding
    - Total amount to be paid
    - Actual interest collected
    - Effective interest rate (after rounding)
    - Rounding error magnitude

    Reference: COMPREHENSIVE_AUDIT_AND_FIXES.md Section 4

    Args:
        principal: Loan amount in rupees
        annual_rate: Annual interest rate (percentage, e.g., 12.0 for 12%)
        months: Loan tenure in months

    Returns:
        {
            'monthly_emi': float (rounded to 2 decimals),
            'total_amount': float (monthly_emi * months),
            'total_interest': float (total_amount - principal),
            'effective_rate': float (actual interest rate after rounding),
            'rounding_error': float (difference from exact EMI),
            'rate_deviation_percent': float (deviation from expected rate)
        }

    Example:
        >>> result = calculate_emi_precise(12499, 12.0, 6)
        >>> print(f"Monthly EMI: ₹{result['monthly_emi']:,.2f}")
        >>> print(f"Total Interest: ₹{result['total_interest']:,.2f}")
        >>> print(f"Effective Rate: {result['effective_rate']:.2f}%")
    """
    if annual_rate == 0:
        # No cost EMI
        exact_emi = principal / months
        monthly_emi = round(exact_emi, 2)
        total_amount = monthly_emi * months

        return {
            'monthly_emi': monthly_emi,
            'total_amount': round(total_amount, 2),
            'total_interest': round(total_amount - principal, 2),
            'effective_rate': 0.0,
            'rounding_error': abs(monthly_emi - exact_emi),
            'rate_deviation_percent': 0.0
        }

    # Calculate exact EMI (high precision)
    monthly_rate = annual_rate / 12 / 100
    rate_multiplier = math.pow(1 + monthly_rate, months)
    exact_emi = principal * monthly_rate * rate_multiplier / (rate_multiplier - 1)

    # Round to 2 decimals (standard practice)
    monthly_emi = round(exact_emi, 2)

    # Calculate totals
    total_amount = monthly_emi * months
    total_interest = total_amount - principal

    # Validate: total amount should not be less than principal
    if total_amount < principal:
        raise ValueError(
            f"EMI calculation error: Total amount (₹{total_amount:,.2f}) "
            f"< Principal (₹{principal:,.2f})"
        )

    # Calculate effective annual rate (after rounding)
    # Effective monthly rate: (total_amount / principal - 1) / months
    effective_monthly_rate = (total_amount / principal - 1) / months
    effective_annual_rate = effective_monthly_rate * 12 * 100

    rounding_error = abs(monthly_emi - exact_emi)

    # Calculate rate deviation percentage
    rate_deviation = abs(effective_annual_rate - annual_rate) / annual_rate if annual_rate > 0 else 0

    # Warn if rounding causes >1% rate deviation
    if rate_deviation > 0.01:
        logger.warning(
            f"High EMI rounding error: Principal=₹{principal:,.0f}, "
            f"Months={months}, Expected Rate={annual_rate}%, "
            f"Effective Rate={effective_annual_rate:.2f}% "
            f"(deviation: {rate_deviation*100:.2f}%)"
        )

    return {
        'monthly_emi': monthly_emi,
        'total_amount': round(total_amount, 2),
        'total_interest': round(total_interest, 2),
        'effective_rate': round(effective_annual_rate, 2),
        'rounding_error': round(rounding_error, 4),
        'rate_deviation_percent': round(rate_deviation * 100, 2)
    }


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
