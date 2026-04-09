"""Prompt templates for Claude-generated credit narratives."""


def get_credit_narrative_prompt(
    user_name: str,
    user_profile: dict,
    credit_score_result: dict,
    purchase_amount: float = 0
) -> str:
    """
    Generate Claude prompt for personalized credit decision narrative.

    Args:
        user_name: User's name
        user_profile: User profile data
        credit_score_result: Credit scoring result
        purchase_amount: Current purchase amount

    Returns:
        Formatted prompt for Claude API
    """
    decision = credit_score_result["decision"]
    credit_tier = credit_score_result["credit_tier"]
    credit_limit = credit_score_result["credit_limit"]
    score_breakdown = credit_score_result["score_breakdown"]
    total_score = credit_score_result["total_score"]
    purchase_amount_from_result = credit_score_result.get("purchase_amount", purchase_amount)

    prompt = f"""You are a financial advisor explaining a BNPL credit decision for GrabOn.

User Profile:
- Name: {user_name}
- Member Since: {user_profile['member_since']}
- Total Purchases: {user_profile['total_purchases']}
- Avg Order Value: ₹{user_profile['avg_order_value']:.2f}
- Return Rate: {user_profile['return_rate']*100:.1f}%
- Categories: {', '.join(user_profile['categories'])}

Credit Decision:
- Tier: {credit_tier}
- Decision: {decision}
- Credit Limit: ₹{credit_limit:,.0f}
- Purchase Amount: ₹{purchase_amount_from_result:,.0f}
- Total Score: {total_score:.1f}/100

Score Breakdown:
- Purchase Frequency: {score_breakdown['purchase_frequency']:.1f}/100
- Return Behavior: {score_breakdown['return_behavior']:.1f}/100
- GMV Trajectory: {score_breakdown['gmv_trajectory']:.1f}/100
- Category Diversity: {score_breakdown['category_diversity']:.1f}/100
- Coupon Redemption: {score_breakdown['coupon_redemption']:.1f}/100
- Fraud Check: {score_breakdown['fraud_check']:.1f}/100

Generate a 2-3 sentence explanation in simple Indian English that a common user can easily understand:

IMPORTANT RULES:
1. Use plain language - NO technical terms like "fraud score", "GMV trajectory", or percentages like "66.7/100"
2. Translate scores into simple descriptions:
   - Instead of "fraud check 100/100" → say "all security checks passed" or omit entirely
   - Instead of "return behavior 89.6/100" → say "very low return rate of 2%"
   - Instead of "category diversity 66.7/100" → say "you shop across 4 different categories"
   - Instead of "coupon usage 92/100" → say "you use coupons smartly"
3. Focus on WHAT THE USER DID (actions), not abstract scores
4. Use specific numbers ONLY for: purchase count, return rate %, credit limit ₹, months as member
5. Keep it warm, encouraging, and actionable

Examples:

APPROVED (Growing User):
"Great news! You've been approved for ₹15,000 credit because you've made 25 purchases with very few returns (0% return rate), and you shop across multiple categories like Fashion, Electronics, and Food. Keep up this responsible shopping pattern!"

APPROVED (Power User):
"You've been approved for a ₹50,000 credit limit! With 237 purchases and zero returns over the past year, you've shown excellent payment discipline. You're one of our most trusted customers."

AMOUNT EXCEEDS LIMIT (Purchase too high):
"This ₹18,000 purchase exceeds your ₹15,000 Pay Later limit. You can either choose a product under ₹15,000 or pay using UPI, Card, or Netbanking for this purchase. Your credit limit will increase as you complete more purchases."

NEW USER:
"Welcome to GrabOn! Since you're new (joined just a week ago), we need to see a few successful purchases first. Complete 3-5 orders over the next month, and we'll unlock Pay Later for you. Meanwhile, use UPI or Card for instant checkout."

NOT ELIGIBLE (High Returns):
"We've noticed 18% of your orders were returned. To qualify for Pay Later, we need to see a more consistent purchase pattern. Try completing your next 3-4 orders without returns, and we'll reassess your eligibility. Use UPI, Card, or Netbanking for now."

NOT ELIGIBLE (Low Score):
"Pay Later is currently not available based on your purchase history. Build a stronger shopping pattern by making regular purchases with low returns, and check back in a few weeks. You can use UPI, Card, or Netbanking for this purchase."

NOT AFFORDABLE (EMI > 50% income):
"Your total monthly EMI commitments would exceed 50% of your income if we approve this purchase. For your financial safety, we recommend paying via UPI, Card, or Netbanking for this purchase. As you complete your current EMI, your Pay Later capacity will increase."

CREDIT EXHAUSTED (Outstanding dues):
"You have ₹18,000 in outstanding Pay Later dues. Your available credit is ₹7,000. Please pay your current dues to increase your available limit, or choose a smaller purchase amount. You can also use UPI, Card, or Netbanking for this purchase."

IMPORTANT GUIDANCE FOR REJECTION MESSAGES:
- For amount_exceeds_limit: Clearly state the purchase amount vs credit limit, suggest lower-priced products OR alternative payment methods
- For new_user: Welcome them, explain the 3-5 purchase requirement, suggest timeline, offer alternative payment methods
- For not_eligible (high returns): State the return rate issue, provide actionable steps to improve, suggest alternative payments
- For not_eligible (other): Explain what's needed to qualify, provide timeline, offer alternative payments
- ALWAYS include "Use UPI, Card, or Netbanking" suggestion for rejected users
- Be encouraging and helpful, not discouraging

Now generate a narrative for this user following these rules:

IMPORTANT: Do not hallucinate or make up an answer.
"""

    return prompt
