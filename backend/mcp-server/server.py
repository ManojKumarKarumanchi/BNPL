"""
GrabOn BNPL MCP Server
Exposes credit scoring tools to Claude via MCP protocol.

Usage:
    python server.py
"""

from fastmcp import FastMCP
import config
from tools.get_user_profile import get_user_profile
from tools.calculate_credit_score import calculate_credit_score
from tools.generate_emi_options import generate_emi_options
from tools.explain_credit_decision import explain_credit_decision
from models import (
    UserProfileResponse,
    CreditScoreResponse,
    EMIOptionsResponse,
    CreditNarrativeResponse,
    HealthCheckResponse
)

# Initialize FastMCP server
mcp = FastMCP(
    name=config.MCP_SERVER_NAME,
    version=config.MCP_SERVER_VERSION,
    instructions="""
    GrabOn BNPL Credit Scoring MCP Server

    This server provides tools for BNPL (Buy Now, Pay Later) credit eligibility decisions.

    Available Tools:
    1. get_user_profile - Fetch user transaction history
    2. calculate_credit_score - Apply 6-factor scoring model
    3. generate_emi_options - Create EMI plans based on credit tier
    4. explain_credit_decision - Generate personalized AI narrative

    Typical workflow:
    1. get_user_profile("USR_SNEHA") → fetch data
    2. calculate_credit_score("USR_SNEHA", 12499) → score user
    3. generate_emi_options("regular", 12499, 25000) → create EMI plans
    4. explain_credit_decision(...) → generate reason

    Credit Tiers:
    - new_user: 0 limit (blocked <7 days)
    - risky: 0 limit (high returns >10%)
    - growing: ₹15K limit (10-30 transactions)
    - regular: ₹25K limit (30-100 transactions)
    - power: ₹50K limit (100+ transactions, VIP)
    """
)


@mcp.tool()
def get_user_profile_tool(user_id: str) -> UserProfileResponse:
    """
    Fetch user profile and transaction history.

    Args:
        user_id: User ID (e.g., "USR_SNEHA", "USR_VIKRAM")

    Returns:
        User profile with transaction history
    """
    print(f"🔍 Fetching profile for {user_id}...")
    return get_user_profile(user_id)


@mcp.tool()
def calculate_credit_score_tool(user_id: str, purchase_amount: float = 0) -> CreditScoreResponse:
    """
    Calculate credit score and eligibility using 6-factor model.

    6 Factors:
    1. Purchase Frequency (30%)
    2. Return Behavior (25%) - >10% returns = rejection
    3. GMV Trajectory (20%)
    4. Category Diversity (10%)
    5. Coupon Redemption (10%)
    6. Fraud Check (5%) - <7 days = blocked

    Args:
        user_id: User ID
        purchase_amount: Purchase amount for this transaction (optional)

    Returns:
        Credit tier, limit, decision, and score breakdown
    """
    print(f"📊 Calculating credit score for {user_id} (amount: ₹{purchase_amount:.2f})...")
    return calculate_credit_score(user_id, purchase_amount)


@mcp.tool()
def generate_emi_options_tool(
    credit_tier: str,
    purchase_amount: float,
    credit_limit: float
) -> EMIOptionsResponse:
    """
    Generate EMI options based on credit tier.

    Tiers & EMI Options:
    - growing: 3, 6 months
    - regular: 3, 6, 9 months
    - power: 3, 6, 9, 12 months (VIP)

    Args:
        credit_tier: User's credit tier ("growing", "regular", "power")
        purchase_amount: Purchase amount
        credit_limit: User's credit limit

    Returns:
        List of EMI options with monthly payments
    """
    print(f"💰 Generating EMI options for {credit_tier} tier (₹{purchase_amount:.2f})...")
    return generate_emi_options(credit_tier, purchase_amount, credit_limit)


@mcp.tool()
def explain_credit_decision_tool(
    user_id: str,
    credit_score_result: CreditScoreResponse,
    user_profile: UserProfileResponse,
    purchase_amount: float = 0
) -> CreditNarrativeResponse:
    """
    Generate personalized credit decision narrative using Claude API.

    Args:
        user_id: User ID
        credit_score_result: Result from calculate_credit_score_tool
        user_profile: Result from get_user_profile_tool
        purchase_amount: Current purchase amount for context (optional)

    Returns:
        AI-generated explanation (2-3 sentences, specific metrics)
    """
    print(f"✍️  Generating AI narrative for {user_id} (amount: ₹{purchase_amount:.2f})...")
    return explain_credit_decision(user_id, credit_score_result, user_profile, purchase_amount)


# Health check endpoint
@mcp.tool()
def health_check() -> HealthCheckResponse:
    """Check MCP server health and database connectivity."""
    from db.manager import get_db

    try:
        db = get_db()

        # Get user count
        user_result = db.execute_one("SELECT COUNT(*) as count FROM users")
        user_count = dict(user_result)["count"]

        # Get transaction count
        txn_result = db.execute_one("SELECT COUNT(*) as count FROM transactions")
        txn_count = dict(txn_result)["count"]

        return HealthCheckResponse(
            status="healthy",
            database="connected",
            users=user_count,
            transactions=txn_count,
            server=config.MCP_SERVER_NAME,
            version=config.MCP_SERVER_VERSION,
            error=None
        )
    except Exception as e:
        return HealthCheckResponse(
            status="unhealthy",
            database="disconnected",
            users=0,
            transactions=0,
            server=config.MCP_SERVER_NAME,
            version=config.MCP_SERVER_VERSION,
            error=str(e)
        )


if __name__ == "__main__":
    print("=" * 80)
    print("🚀 GrabOn BNPL MCP Server")
    print("=" * 80)
    print(f"Name: {config.MCP_SERVER_NAME}")
    print(f"Version: {config.MCP_SERVER_VERSION}")
    print(f"Database: {config.DB_PATH}")
    print(f"Port: {config.MCP_SERVER_PORT}")
    print("=" * 80)
    print("\n✅ Server ready. Use FastMCP to run this server.")
    print("💡 Tools registered: 5")
    print("   1. get_user_profile_tool")
    print("   2. calculate_credit_score_tool")
    print("   3. generate_emi_options_tool")
    print("   4. explain_credit_decision_tool")
    print("   5. health_check")
    print("\n📚 See README.md for usage examples\n")

    # Run server
    mcp.run()
