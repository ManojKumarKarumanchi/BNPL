"""
Checkout routes - Main BNPL eligibility endpoint.
"""

import logging
from fastapi import APIRouter, HTTPException
from api.schemas.request_schemas import EligibilityRequest
from api.schemas.response_schemas import (
    EligibilityResponse,
    TransactionHistory,
    EMIOption
)
from api.services.mcp_client import get_mcp_client
from api.services.payu_client import get_payu_client
from api.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/checkout", tags=["checkout"])


@router.post("/eligibility", response_model=EligibilityResponse)
async def check_eligibility(request: EligibilityRequest):
    """
    Check BNPL eligibility for a user at checkout.

    This endpoint:
    1. Fetches user profile and transaction history
    2. Calculates credit score using 6-factor model
    3. Generates EMI options (if approved)
    4. Creates AI-powered explanation

    Returns:
        EligibilityResponse with credit decision and EMI plans
    """
    mcp = get_mcp_client()

    try:
        # Step 1: Get user profile
        print(f"Fetching profile for {request.user_id}...")
        user_profile = await mcp.call_tool(
            "get_user_profile_tool",
            {"user_id": request.user_id}
        )
        print(f"Profile fetched: {user_profile.get('name', 'N/A')}")

        if user_profile.get("error"):
            raise HTTPException(
                status_code=404,
                detail=f"User not found: {request.user_id}"
            )

        # Step 2: Calculate credit score
        credit_score = await mcp.call_tool(
            "calculate_credit_score_tool",
            {
                "user_id": request.user_id,
                "purchase_amount": request.amount
            }
        )

        # Step 3: Generate EMI options (if approved)
        emi_options = None
        if credit_score["decision"] == "approved":
            # Try PayU LazyPay API first (if enabled)
            if settings.PAYU_ENABLED:
                try:
                    payu_client = get_payu_client()
                    logger.info(f"💳 Using PayU client: {type(payu_client).__name__}")
                    payu_result = await payu_client.calculate_emi_offers(
                        user_id=request.user_id,
                        amount=request.amount,
                        credit_limit=credit_score["credit_limit"],
                        email=user_profile.get("email")
                    )

                    if payu_result["status"] == "success" and payu_result["emi_options"]:
                        logger.info(f"✅ PayU API success: {len(payu_result['emi_options'])} EMI options")
                        emi_options = [
                            EMIOption(**emi) for emi in payu_result["emi_options"]
                        ]
                    else:
                        logger.warning(f"⚠️ PayU API failed: {payu_result.get('error')}, falling back to local calculation")
                        raise Exception("PayU API returned no options")

                except Exception as e:
                    logger.error(f"❌ PayU API error: {str(e)}, using fallback")
                    # Fallback to local EMI calculation
                    emi_result = await mcp.call_tool(
                        "generate_emi_options_tool",
                        {
                            "credit_tier": credit_score["credit_tier"],
                            "purchase_amount": request.amount,
                            "credit_limit": credit_score["credit_limit"]
                        }
                    )
                    emi_options = [
                        EMIOption(**emi) for emi in emi_result.get("emi_options", [])
                    ]
            else:
                # PayU disabled - use local EMI calculation
                logger.info("📊 Using local EMI calculation (PayU disabled)")
                emi_result = await mcp.call_tool(
                    "generate_emi_options_tool",
                    {
                        "credit_tier": credit_score["credit_tier"],
                        "purchase_amount": request.amount,
                        "credit_limit": credit_score["credit_limit"]
                    }
                )
                emi_options = [
                    EMIOption(**emi) for emi in emi_result.get("emi_options", [])
                ]

        # Step 4: Generate AI narrative (with purchase amount context)
        narrative_result = await mcp.call_tool(
            "explain_credit_decision_tool",
            {
                "user_id": request.user_id,
                "credit_score_result": credit_score,
                "user_profile": user_profile,
                "purchase_amount": request.amount
            }
        )

        # Build response
        response = EligibilityResponse(
            status=credit_score["decision"],
            credit_limit=credit_score["credit_limit"],
            reason=narrative_result["reason"],
            transaction_history=TransactionHistory(
                total_purchases=user_profile["total_purchases"],
                avg_order_value=user_profile["avg_order_value"],
                return_rate=user_profile["return_rate"] * 100,  # Convert to percentage
                member_since=user_profile["member_since"]
            ),
            emi_options=emi_options,
            payu_transaction_id=payu_result.get("transaction_id") if settings.PAYU_ENABLED and 'payu_result' in locals() else None,
            # emi_provider: PayU LazyPay (strategic partner)
            # GrabOn has strategic partnership with PayU for BNPL offering
            emi_provider="PayU LazyPay" if settings.PAYU_ENABLED and 'payu_result' in locals() and payu_result.get("status") == "success" else "PayU LazyPay",
            score_details=credit_score.get("score_breakdown")  # Optional debug info
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
