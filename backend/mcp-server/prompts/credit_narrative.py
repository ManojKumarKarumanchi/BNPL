"""Prompt templates for Claude-generated credit narratives."""


def get_credit_narrative_prompt(
    user_name: str,
    user_profile: dict,
    credit_score_result: dict
) -> str:
    """
    Generate Claude prompt for personalized credit decision narrative.

    Args:
        user_name: User's name
        user_profile: User profile data
        credit_score_result: Credit scoring result

    Returns:
        Formatted prompt for Claude API
    """
    decision = credit_score_result["decision"]
    credit_tier = credit_score_result["credit_tier"]
    credit_limit = credit_score_result["credit_limit"]
    score_breakdown = credit_score_result["score_breakdown"]
    total_score = credit_score_result["total_score"]

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
- Total Score: {total_score:.1f}/100

Score Breakdown:
- Purchase Frequency: {score_breakdown['purchase_frequency']:.1f}/100
- Return Behavior: {score_breakdown['return_behavior']:.1f}/100
- GMV Trajectory: {score_breakdown['gmv_trajectory']:.1f}/100
- Category Diversity: {score_breakdown['category_diversity']:.1f}/100
- Coupon Redemption: {score_breakdown['coupon_redemption']:.1f}/100
- Fraud Check: {score_breakdown['fraud_check']:.1f}/100

Generate a 2-3 sentence explanation in Indian English that:
1. States WHY this decision was made (use specific numbers from above)
2. Highlights the user's strengths (if approved)
3. If rejected/new user: gives actionable advice on what to do next

Tone: Warm, transparent, encouraging. Address user as "you".
Avoid generic phrases like "based on your profile". Focus on specific metrics.
Keep it under 100 words.

Examples:

APPROVED (Regular User):
"Based on your frequent purchases, low return rate of 2%, and consistent spending over the past 6 months, you've been pre-approved for instant credit. Your track record of 48 completed orders demonstrates reliability, earning you a ₹25,000 credit limit."

NEW USER:
"You're new to GrabOn! Complete 3-5 purchases over the next few weeks to unlock Pay Later benefits and build your credit profile with us."

REJECTED (High Returns):
"Our system detected irregular purchase patterns and a high return rate (18%). We need to see more consistent activity before enabling Pay Later for your account."

Now generate for this user:"""

    return prompt
