"""
MCP Tool: Explain Credit Decision
Generates personalized AI narrative using Claude API.
"""

from typing import Dict, Any
from prompts.credit_narrative import get_credit_narrative_prompt
from utils.claude_client import ClaudeClient


def explain_credit_decision(
    user_id: str,
    credit_score_result: Dict[str, Any],
    user_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate personalized credit decision narrative.

    Args:
        user_id: User ID
        credit_score_result: Result from calculate_credit_score
        user_profile: Result from get_user_profile

    Returns:
        {
            "reason": str,  # AI-generated narrative
            "error": None
        }
    """
    try:
        # Handle rejection reasons (no Claude API needed)
        if credit_score_result.get("rejection_reason"):
            return {
                "reason": credit_score_result["rejection_reason"],
                "error": None
            }

        # Generate prompt
        prompt = get_credit_narrative_prompt(
            user_name=user_profile["name"],
            user_profile=user_profile,
            credit_score_result=credit_score_result
        )

        # Call Claude API
        claude_client = ClaudeClient()
        narrative = claude_client.generate_narrative(prompt, max_tokens=150)

        return {
            "reason": narrative.strip(),
            "error": None
        }

    except Exception as e:
        # Fallback to template-based narrative
        decision = credit_score_result.get("decision", "approved")
        credit_limit = credit_score_result.get("credit_limit", 0)

        fallback_narratives = {
            "approved": f"You've been pre-approved for a credit limit of ₹{credit_limit:,.0f} based on your purchase history and payment behavior.",
            "new_user": "Complete a few purchases to unlock Pay Later benefits.",
            "not_eligible": "Pay Later is not available at this time based on your transaction patterns."
        }

        return {
            "reason": fallback_narratives.get(decision, "Credit decision processed."),
            "error": f"Claude API error: {str(e)} (using fallback)"
        }
