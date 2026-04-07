"""
MCP Tool: Calculate Credit Score
Applies 6-factor scoring model to user profile.
"""

from typing import Dict, Any
from tools.get_user_profile import get_user_profile
from utils.scoring_engine import CreditScoringEngine


def calculate_credit_score(
    user_id: str,
    purchase_amount: float = 0
) -> Dict[str, Any]:
    """
    Calculate credit score and eligibility for user.

    Args:
        user_id: User ID (e.g., "USR_SNEHA")
        purchase_amount: Purchase amount for this transaction (optional)

    Returns:
        {
            "user_id": str,
            "credit_tier": str,  # "new_user", "risky", "growing", "regular", "power"
            "credit_limit": float,
            "decision": str,  # "approved", "not_eligible", "new_user"
            "total_score": float,
            "rejection_reason": str | None,
            "score_breakdown": {
                "purchase_frequency": float,
                "return_behavior": float,
                "gmv_trajectory": float,
                "category_diversity": float,
                "coupon_redemption": float,
                "fraud_check": float
            },
            "error": None
        }
    """
    # Fetch user profile
    user_profile = get_user_profile(user_id)

    if user_profile.get("error"):
        return {
            "error": user_profile["error"],
            "user_id": user_id
        }

    # Initialize scoring engine
    scoring_engine = CreditScoringEngine()

    # Calculate credit score
    score_result = scoring_engine.calculate_composite_score(
        user_profile=user_profile,
        transactions=user_profile["transactions"]
    )

    # Add user_id to result
    score_result["user_id"] = user_id

    return score_result
