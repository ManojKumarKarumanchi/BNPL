"""
MCP Tool: Explain Credit Decision
Generates personalized AI narrative using Claude API or Azure OpenAI.

Supports both AI providers via AI_PROVIDER environment variable.
"""

import logging
from typing import Dict, Any, Union
from prompts.credit_narrative import get_credit_narrative_prompt
from utils.claude_client import get_ai_client
from models import CreditNarrativeResponse, CreditScoreResponse, UserProfileResponse
import config

logger = logging.getLogger(__name__)


def explain_credit_decision(
    user_id: str,
    credit_score_result: Union[Dict[str, Any], CreditScoreResponse],
    user_profile: Union[Dict[str, Any], UserProfileResponse],
    purchase_amount: float = 0
) -> CreditNarrativeResponse:
    """
    Generate personalized credit decision narrative.

    Args:
        user_id: User ID
        credit_score_result: Result from calculate_credit_score (dict or Pydantic model)
        user_profile: Result from get_user_profile (dict or Pydantic model)
        purchase_amount: Current purchase amount for context

    Returns:
        CreditNarrativeResponse with AI-generated explanation and error field if failed
    """
    try:
        # Convert dicts to Pydantic models if needed
        if isinstance(credit_score_result, dict):
            credit_score_result = CreditScoreResponse(**credit_score_result)
        if isinstance(user_profile, dict):
            user_profile = UserProfileResponse(**user_profile)

        decision = credit_score_result.decision
        credit_limit = credit_score_result.credit_limit
        purchase_amt = credit_score_result.purchase_amount or purchase_amount

        logger.info(f"Generating narrative for {user_id}: decision={decision}, limit=₹{credit_limit}, amount=₹{purchase_amt}")

        # For simple rejection reasons with clear context, use AI to enhance the message
        # But for amount_exceeds_limit with rejection_reason, we want AI to personalize it
        if credit_score_result.rejection_reason and decision != "amount_exceeds_limit":
            # Use AI to enhance rejection messages (not just return raw rejection_reason)
            logger.info(f"Rejection reason exists: {credit_score_result.rejection_reason}")

        # Generate prompt with purchase amount context
        prompt = get_credit_narrative_prompt(
            user_name=user_profile.name,
            user_profile=user_profile.model_dump(),
            credit_score_result=credit_score_result.model_dump(),
            purchase_amount=purchase_amt
        )

        # Call AI API (Claude or Azure OpenAI based on AI_PROVIDER config)
        ai_client = get_ai_client()
        narrative = ai_client.generate_narrative(prompt, max_tokens=200)

        logger.info(f"✅ AI narrative generated using {config.AI_PROVIDER.upper()}")

        return CreditNarrativeResponse(
            user_id=user_id,
            reason=narrative.strip(),
            status=decision,
            error=None
        )

    except Exception as e:
        logger.exception(f"Failed to generate AI narrative for {user_id}")

        # Fallback to enhanced template-based narratives
        decision = credit_score_result.decision
        credit_limit = credit_score_result.credit_limit
        purchase_amt = credit_score_result.purchase_amount or purchase_amount
        return_rate = user_profile.return_rate if hasattr(user_profile, 'return_rate') else 0

        fallback_narratives = {
            "approved": f"You've been pre-approved for a credit limit of ₹{credit_limit:,.0f} based on your purchase history and responsible shopping behavior.",

            "amount_exceeds_limit": f"This ₹{purchase_amt:,.0f} purchase exceeds your ₹{credit_limit:,.0f} Pay Later limit. You can either choose a product under ₹{credit_limit:,.0f} or pay using UPI, Card, or Netbanking for this purchase.",

            "new_user": "Welcome to GrabOn! To unlock Pay Later, complete 3-5 successful purchases over the next few weeks. This helps us understand your shopping pattern. Meanwhile, use UPI or Card for instant checkout.",

            "not_eligible": f"Pay Later is currently not available. {'Try completing your next few orders without returns to qualify.' if return_rate > 0.10 else 'Build your purchase history with us and check back soon.'} Use UPI, Card, or Netbanking for this purchase."
        }

        return CreditNarrativeResponse(
            user_id=user_id,
            reason=fallback_narratives.get(decision, "Pay Later is not available at this time. Use UPI, Card, or Netbanking for this purchase."),
            status=decision,
            error=f"AI API error ({config.AI_PROVIDER}): {str(e)} (using fallback)"
        )
