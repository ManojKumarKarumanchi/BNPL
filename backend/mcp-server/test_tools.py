"""
Quick test script for MCP tools.
Tests credit scoring for all 5 personas.
"""

import sys
sys.path.insert(0, '.')

from tools.get_user_profile import get_user_profile
from tools.calculate_credit_score import calculate_credit_score
from tools.generate_emi_options import generate_emi_options

def test_persona(user_id, expected_tier):
    """Test credit scoring for a persona."""
    print(f"\n{'='*80}")
    print(f"Testing: {user_id}")
    print("="*80)

    # Step 1: Get user profile
    profile = get_user_profile(user_id)
    if profile.get("error"):
        print(f"❌ Error: {profile['error']}")
        return

    print(f"✅ User: {profile['name']}")
    print(f"   Transactions: {profile['total_purchases']}")
    print(f"   Avg Order: ₹{profile['avg_order_value']:.2f}")
    print(f"   Return Rate: {profile['return_rate']*100:.1f}%")

    # Step 2: Calculate credit score
    score_result = calculate_credit_score(user_id, 12499)

    print(f"\n📊 Credit Scoring Result:")
    print(f"   Tier: {score_result['credit_tier']} (expected: {expected_tier})")
    print(f"   Limit: ₹{score_result['credit_limit']:,}")
    print(f"   Decision: {score_result['decision']}")
    print(f"   Total Score: {score_result.get('total_score', 0):.1f}/100")

    if score_result.get("rejection_reason"):
        print(f"   ❌ Rejection: {score_result['rejection_reason']}")

    # Score breakdown
    if score_result.get("score_breakdown"):
        print(f"\n   Score Breakdown:")
        breakdown = score_result["score_breakdown"]
        print(f"     Purchase Frequency: {breakdown['purchase_frequency']:.1f}/100")
        print(f"     Return Behavior: {breakdown['return_behavior']:.1f}/100")
        print(f"     GMV Trajectory: {breakdown['gmv_trajectory']:.1f}/100")
        print(f"     Category Diversity: {breakdown['category_diversity']:.1f}/100")
        print(f"     Coupon Redemption: {breakdown['coupon_redemption']:.1f}/100")
        print(f"     Fraud Check: {breakdown['fraud_check']:.1f}/100")

    # Step 3: Generate EMI options (if approved)
    if score_result['decision'] == 'approved':
        emi_result = generate_emi_options(
            credit_tier=score_result['credit_tier'],
            purchase_amount=12499,
            credit_limit=score_result['credit_limit']
        )

        if emi_result['emi_options']:
            print(f"\n💰 EMI Options: {len(emi_result['emi_options'])} plans")
            for emi in emi_result['emi_options']:
                tag = f" ({emi['tag']})" if emi['tag'] else ""
                print(f"     {emi['duration']} months: ₹{emi['monthly_payment']}/mo{tag}")

    # Validation
    if score_result['credit_tier'] == expected_tier:
        print(f"\n✅ PASS: Tier matches expected ({expected_tier})")
    else:
        print(f"\n❌ FAIL: Expected {expected_tier}, got {score_result['credit_tier']}")


def main():
    """Test all personas."""
    print("\n" + "="*80)
    print("GrabOn BNPL MCP Tools - Credit Scoring Test")
    print("="*80)

    personas = [
        ("USR_RAJESH", "new_user"),
        ("USR_PRIYA", "risky"),
        ("USR_AMIT", "growing"),
        ("USR_SNEHA", "regular"),
        ("USR_VIKRAM", "power")
    ]

    results = []
    for user_id, expected_tier in personas:
        test_persona(user_id, expected_tier)
        results.append((user_id, expected_tier))

    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    print("All 5 personas tested. Review output above for detailed results.")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
