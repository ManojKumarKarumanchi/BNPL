"""
MCP Tool: Calculate Credit Score
Applies 6-factor scoring model to user profile.
"""

import logging
from typing import Dict, Any
from tools.get_user_profile import get_user_profile
from utils.scoring_engine import CreditScoringEngine
from models import CreditScoreResponse, ScoreBreakdown
from validators import validate_user_id, validate_purchase_amount, ValidationError
import config

logger = logging.getLogger(__name__)


def calculate_credit_score(
    user_id: str,
    purchase_amount: float = 0
) -> CreditScoreResponse:
    """
    Calculate credit score and eligibility for user.

    Args:
        user_id: User ID (e.g., "USR_SNEHA")
        purchase_amount: Purchase amount for this transaction (optional)

    Returns:
        CreditScoreResponse with score breakdown and error field if failed
    """
    try:
        # Validate inputs
        validate_user_id(user_id)
        if purchase_amount > 0:
            validate_purchase_amount(purchase_amount)

        logger.info(f"Calculating credit score for user: {user_id}, amount: ₹{purchase_amount}")

        # Fetch user profile
        user_profile = get_user_profile(user_id)

        if user_profile.error:
            logger.warning(f"User profile error for {user_id}: {user_profile.error}")
            return CreditScoreResponse(
                user_id=user_id,
                credit_tier="risky",
                credit_limit=0.0,
                decision="not_eligible",
                score_breakdown=ScoreBreakdown(
                    purchase_frequency=0.0,
                    return_behavior=0.0,
                    gmv_trajectory=0.0,
                    category_diversity=0.0,
                    coupon_redemption=0.0,
                    fraud_check=0.0
                ),
                error=user_profile.error
            )

        # Initialize scoring engine
        scoring_engine = CreditScoringEngine()

        # Calculate credit score (with purchase amount validation)
        score_result = scoring_engine.calculate_composite_score(
            user_profile=user_profile.model_dump(),
            transactions=user_profile.transactions,
            purchase_amount=purchase_amount
        )

        decision = score_result['decision']
        logger.info(f"Credit score calculated: {score_result.get('total_score', 0.0)}, tier: {score_result['credit_tier']}, decision: {decision}")

        # Create Pydantic response
        return CreditScoreResponse(
            user_id=user_id,
            total_score=score_result.get("total_score", 0.0),
            credit_tier=score_result["credit_tier"],
            credit_limit=score_result["credit_limit"],
            decision=score_result["decision"],
            rejection_reason=score_result.get("rejection_reason"),
            purchase_amount=score_result.get("purchase_amount", purchase_amount),
            score_breakdown=ScoreBreakdown(**score_result["score_breakdown"]),
            min_transactions=config.FRAUD_THRESHOLDS.get("min_transactions", 10),
            error=None
        )

    except ValidationError as e:
        logger.error(f"Validation error for {user_id}: {e}")
        return CreditScoreResponse(
            user_id=user_id,
            total_score=0.0,
            credit_tier="risky",
            credit_limit=0.0,
            decision="not_eligible",
            score_breakdown=ScoreBreakdown(
                purchase_frequency=0.0,
                return_behavior=0.0,
                gmv_trajectory=0.0,
                category_diversity=0.0,
                coupon_redemption=0.0,
                fraud_check=0.0
            ),
            error=str(e)
        )
    except Exception as e:
        logger.exception(f"Unexpected error calculating credit score for {user_id}")
        return CreditScoreResponse(
            user_id=user_id,
            total_score=0.0,
            credit_tier="risky",
            credit_limit=0.0,
            decision="not_eligible",
            score_breakdown=ScoreBreakdown(
                purchase_frequency=0.0,
                return_behavior=0.0,
                gmv_trajectory=0.0,
                category_diversity=0.0,
                coupon_redemption=0.0,
                fraud_check=0.0
            ),
            error=f"Internal error: {str(e)}"
        )
