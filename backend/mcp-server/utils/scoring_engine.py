"""
6-Factor Credit Scoring Engine for GrabOn BNPL.
Data-driven, explainable scoring model.
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import config


class CreditScoringEngine:
    """
    Implements 6-factor credit scoring model:
    1. Purchase Frequency (30%) - Transactions per month
    2. Return Behavior (25%) - Inverse of return rate (>10% = rejection)
    3. GMV Trajectory (20%) - Spending trend over time
    4. Category Diversification (10%) - Unique categories (1-6)
    5. Coupon Redemption Rate (10%) - Quality signal
    6. Fraud Check (5%) - New users (<7 days) blocked
    """

    def __init__(self):
        self.weights = config.SCORING_WEIGHTS
        self.fraud_thresholds = config.FRAUD_THRESHOLDS
        self.credit_tiers = config.CREDIT_TIERS

    def calculate_purchase_frequency_score(
        self,
        total_purchases: int,
        member_since: datetime
    ) -> float:
        """
        Score based on transaction frequency.
        Weight: 30%
        Formula: min(100, (total_purchases / months_active) * 10)
        """
        days_active = (datetime.now() - member_since).days
        months_active = max(1, days_active / 30)

        txns_per_month = total_purchases / months_active

        # Scale: 10 txns/month = 100 points
        score = min(100, txns_per_month * 10)

        return score

    def calculate_return_behavior_score(self, return_rate: float) -> Dict[str, Any]:
        """
        Score based on return rate (inverse).
        Weight: 25%
        Formula: max(0, 100 - (return_rate * 500))
        Rejection Rule: return_rate > 10% → instant rejection
        """
        is_rejected = return_rate > self.fraud_thresholds["max_return_rate"]

        if is_rejected:
            return {
                "score": 0,
                "rejected": True,
                "reason": f"High return rate detected: {return_rate*100:.1f}%"
            }

        # Good return behavior = high score
        score = max(0, 100 - (return_rate * 500))

        return {
            "score": score,
            "rejected": False,
            "reason": None
        }

    def calculate_gmv_trajectory_score(
        self,
        transactions: List[Dict[str, Any]]
    ) -> float:
        """
        Score based on GMV trend over time (linear regression slope).
        Weight: 20%
        Formula: 50 + (slope * 10) (normalized 0-100)
        """
        if len(transactions) < 3:
            return 50  # Neutral score for insufficient data

        # Group transactions by month
        monthly_gmv = {}
        for txn in transactions:
            txn_date = datetime.strptime(txn["transaction_date"], "%Y-%m-%d")
            month_key = txn_date.strftime("%Y-%m")

            if month_key not in monthly_gmv:
                monthly_gmv[month_key] = 0

            monthly_gmv[month_key] += txn["final_amount"]

        # Calculate trend (simple linear regression)
        months = sorted(monthly_gmv.keys())
        if len(months) < 2:
            return 50

        gmv_values = [monthly_gmv[m] for m in months]
        x = np.arange(len(gmv_values))
        y = np.array(gmv_values)

        # Linear fit
        slope = np.polyfit(x, y, 1)[0]

        # Normalize slope to 0-100 scale
        # Positive slope = increasing GMV = good
        score = 50 + min(50, max(-50, slope / 100))

        return score

    def calculate_category_diversity_score(
        self,
        transactions: List[Dict[str, Any]]
    ) -> float:
        """
        Score based on unique categories.
        Weight: 10%
        Formula: min(100, unique_categories * 16.67)
        """
        if not transactions:
            return 0

        unique_categories = len(set(txn["category"] for txn in transactions))

        # 6 categories = 100 points (max diversity)
        score = min(100, unique_categories * 16.67)

        return score

    def calculate_coupon_redemption_score(
        self,
        transactions: List[Dict[str, Any]]
    ) -> float:
        """
        Score based on coupon redemption rate.
        Weight: 10%
        Formula: (coupons_used / total_purchases) * 100
        """
        if not transactions:
            return 0

        coupons_used = sum(1 for txn in transactions if txn["coupon_used"])
        redemption_rate = (coupons_used / len(transactions)) * 100

        return redemption_rate

    def calculate_fraud_check_score(
        self,
        member_since: datetime,
        total_purchases: int
    ) -> Dict[str, Any]:
        """
        Fraud detection based on membership tenure and velocity.
        Weight: 5%
        New users (<7 days) are blocked
        """
        days_since_joined = (datetime.now() - member_since).days

        # Fraud Rule 1: New user blocking
        if days_since_joined < self.fraud_thresholds["min_days_membership"]:
            return {
                "score": -100,  # Penalty
                "blocked": True,
                "reason": f"Account too new ({days_since_joined} days). Complete 3-5 purchases first."
            }

        # Fraud Rule 2: Velocity check (future enhancement)
        # if total_purchases > 50 and days_since_joined < 30:
        #     return {"score": -50, "blocked": True, "reason": "Suspicious velocity"}

        return {
            "score": 100,  # Pass
            "blocked": False,
            "reason": None
        }

    def calculate_composite_score(
        self,
        user_profile: Dict[str, Any],
        transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate final credit score using weighted 6-factor model.
        Returns credit tier, limit, and score breakdown.
        """
        # Extract user data
        member_since = datetime.strptime(user_profile["member_since"], "%Y-%m-%d")
        total_purchases = user_profile["total_purchases"]
        return_rate = user_profile["return_rate"]

        # Factor 1: Purchase Frequency (30%)
        freq_score = self.calculate_purchase_frequency_score(
            total_purchases, member_since
        )

        # Factor 2: Return Behavior (25%)
        return_result = self.calculate_return_behavior_score(return_rate)
        if return_result["rejected"]:
            return {
                "credit_tier": "risky",
                "credit_limit": 0,
                "decision": "not_eligible",
                "total_score": 0,
                "rejection_reason": return_result["reason"],
                "score_breakdown": {
                    "purchase_frequency": freq_score,
                    "return_behavior": 0,
                    "gmv_trajectory": 0,
                    "category_diversity": 0,
                    "coupon_redemption": 0,
                    "fraud_check": 0
                }
            }

        # Factor 3: GMV Trajectory (20%)
        gmv_score = self.calculate_gmv_trajectory_score(transactions)

        # Factor 4: Category Diversity (10%)
        category_score = self.calculate_category_diversity_score(transactions)

        # Factor 5: Coupon Redemption (10%)
        coupon_score = self.calculate_coupon_redemption_score(transactions)

        # Factor 6: Fraud Check (5%)
        fraud_result = self.calculate_fraud_check_score(member_since, total_purchases)
        if fraud_result["blocked"]:
            return {
                "credit_tier": "new_user",
                "credit_limit": 0,
                "decision": "new_user",
                "total_score": 0,
                "rejection_reason": fraud_result["reason"],
                "score_breakdown": {
                    "purchase_frequency": freq_score,
                    "return_behavior": return_result["score"],
                    "gmv_trajectory": gmv_score,
                    "category_diversity": category_score,
                    "coupon_redemption": coupon_score,
                    "fraud_check": fraud_result["score"]
                }
            }

        # Calculate weighted total score
        total_score = (
            freq_score * self.weights["purchase_frequency"] +
            return_result["score"] * self.weights["return_behavior"] +
            gmv_score * self.weights["gmv_trajectory"] +
            category_score * self.weights["category_diversity"] +
            coupon_score * self.weights["coupon_redemption"] +
            fraud_result["score"] * self.weights["fraud_check"]
        )

        # Map score to credit tier
        credit_tier = self.map_score_to_tier(total_score, total_purchases)

        return {
            "credit_tier": credit_tier,
            "credit_limit": self.credit_tiers[credit_tier]["credit_limit"],
            "decision": "approved" if self.credit_tiers[credit_tier]["credit_limit"] > 0 else "not_eligible",
            "total_score": round(total_score, 2),
            "rejection_reason": None,
            "score_breakdown": {
                "purchase_frequency": round(freq_score, 2),
                "return_behavior": round(return_result["score"], 2),
                "gmv_trajectory": round(gmv_score, 2),
                "category_diversity": round(category_score, 2),
                "coupon_redemption": round(coupon_score, 2),
                "fraud_check": round(fraud_result["score"], 2)
            }
        }

    def map_score_to_tier(self, score: float, total_purchases: int) -> str:
        """
        Map composite score to credit tier.
        Tier progression: new_user → risky → growing → regular → power
        """
        # Power User: Score >= 85 AND 100+ transactions
        if score >= 85 and total_purchases >= 100:
            return "power"

        # Regular User: Score >= 70 AND 30+ transactions
        if score >= 70 and total_purchases >= 30:
            return "regular"

        # Growing User: Score >= 55 AND 10+ transactions
        if score >= 55 and total_purchases >= self.fraud_thresholds["min_transactions"]:
            return "growing"

        # Risky: Low score or insufficient transactions
        return "risky"
