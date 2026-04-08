"""
MCP Tool: Generate EMI Options
Creates EMI plans based on credit tier and purchase amount.
"""

from typing import Dict, List, Any
from utils.emi_calculator import generate_emi_plans
from models import EMIOptionsResponse, EMIOption


def generate_emi_options(
    credit_tier: str,
    purchase_amount: float,
    credit_limit: float
) -> EMIOptionsResponse:
    """
    Generate EMI options for approved users.

    Args:
        credit_tier: User's credit tier ("growing", "regular", "power")
        purchase_amount: Purchase amount
        credit_limit: User's credit limit

    Returns:
        EMIOptionsResponse with list of EMI plans and error field if failed
    """
    try:
        emi_plans = generate_emi_plans(
            purchase_amount=purchase_amount,
            credit_tier=credit_tier,
            credit_limit=credit_limit
        )

        # Convert to Pydantic models
        emi_options = [EMIOption(**plan) for plan in emi_plans]

        return EMIOptionsResponse(
            emi_options=emi_options,
            credit_tier=credit_tier,
            credit_limit=credit_limit,
            purchase_amount=purchase_amount,
            error=None
        )

    except Exception as e:
        return EMIOptionsResponse(
            emi_options=[],
            credit_tier=credit_tier,
            credit_limit=credit_limit,
            purchase_amount=purchase_amount,
            error=f"EMI calculation error: {str(e)}"
        )
