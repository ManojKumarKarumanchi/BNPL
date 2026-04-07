"""
MCP Tool: Generate EMI Options
Creates EMI plans based on credit tier and purchase amount.
"""

from typing import Dict, List, Any
from utils.emi_calculator import generate_emi_plans


def generate_emi_options(
    credit_tier: str,
    purchase_amount: float,
    credit_limit: float
) -> Dict[str, Any]:
    """
    Generate EMI options for approved users.

    Args:
        credit_tier: User's credit tier ("growing", "regular", "power")
        purchase_amount: Purchase amount
        credit_limit: User's credit limit

    Returns:
        {
            "emi_options": List[Dict],
            "error": None
        }
    """
    try:
        emi_options = generate_emi_plans(
            purchase_amount=purchase_amount,
            credit_tier=credit_tier,
            credit_limit=credit_limit
        )

        return {
            "emi_options": emi_options,
            "error": None
        }

    except Exception as e:
        return {
            "emi_options": [],
            "error": f"EMI calculation error: {str(e)}"
        }
