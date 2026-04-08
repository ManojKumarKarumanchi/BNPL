"""
Quick test to verify MCP client fix for UserProfileResponse.get() issue.
"""

import sys
import asyncio
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def test_mcp_client():
    """Test that MCP client returns dicts, not Pydantic models."""
    from api.services.mcp_client import get_mcp_client

    mcp = get_mcp_client()

    # Test 1: get_user_profile should return a dict
    print("Test 1: Testing get_user_profile...")
    user_profile = await mcp.call_tool(
        "get_user_profile_tool",
        {"user_id": "USR_AMIT"}
    )

    print(f"  Type: {type(user_profile)}")
    print(f"  Is dict: {isinstance(user_profile, dict)}")

    if isinstance(user_profile, dict):
        print(f"  ✓ Returns dict (can use .get())")
        print(f"  User name: {user_profile.get('name', 'N/A')}")
    else:
        print(f"  ✗ ERROR: Returns {type(user_profile)} (cannot use .get())")
        return False

    # Test 2: calculate_credit_score should return a dict
    print("\nTest 2: Testing calculate_credit_score...")
    credit_score = await mcp.call_tool(
        "calculate_credit_score_tool",
        {
            "user_id": "USR_AMIT",
            "purchase_amount": 12499
        }
    )

    print(f"  Type: {type(credit_score)}")
    print(f"  Is dict: {isinstance(credit_score, dict)}")

    if isinstance(credit_score, dict):
        print(f"  ✓ Returns dict (can use .get())")
        print(f"  Decision: {credit_score.get('decision')}")
        print(f"  Credit limit: {credit_score.get('credit_limit')}")
    else:
        print(f"  ✗ ERROR: Returns {type(credit_score)} (cannot use .get())")
        return False

    # Test 3: explain_credit_decision should accept dicts
    print("\nTest 3: Testing explain_credit_decision...")
    narrative = await mcp.call_tool(
        "explain_credit_decision_tool",
        {
            "user_id": "USR_AMIT",
            "credit_score_result": credit_score,  # Passing dict
            "user_profile": user_profile  # Passing dict
        }
    )

    print(f"  Type: {type(narrative)}")
    print(f"  Is dict: {isinstance(narrative, dict)}")

    if isinstance(narrative, dict):
        print(f"  ✓ Returns dict")
        print(f"  Reason: {narrative.get('reason', 'N/A')[:100]}...")
    else:
        print(f"  ✗ ERROR: Returns {type(narrative)}")
        return False

    print("\n" + "=" * 80)
    print("✓ All tests passed! MCP client fix is working correctly.")
    print("=" * 80)
    return True

if __name__ == "__main__":
    asyncio.run(test_mcp_client())
