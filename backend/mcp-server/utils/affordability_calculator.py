"""
Affordability Calculator - Implements 50% EMI-to-Income Rule.

Calculates whether user can afford new EMI based on:
1. Monthly income
2. Current EMI commitments
3. Proposed new EMI
4. Industry standard: Total EMI ≤ 50% of income (RBI guidelines)
"""

from typing import Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AffordabilityCalculator:
    """Calculates EMI affordability based on income and existing commitments."""

    # Industry standard: Total monthly EMI should not exceed 50% of income
    # Reference: RBI guidelines for responsible lending
    MAX_EMI_TO_INCOME_RATIO = 0.50

    @staticmethod
    def calculate_current_emi_burden(user_id: str, db_manager) -> float:
        """
        Calculate total current monthly EMI commitments for user.

        Queries active EMI commitments from database and sums monthly payments.
        Only includes commitments where end_date >= current date (active loans).

        Args:
            user_id: User identifier
            db_manager: Database manager instance

        Returns:
            Total monthly EMI amount (float)

        Example:
            >>> db = get_db()
            >>> current_emi = AffordabilityCalculator.calculate_current_emi_burden('USR_SNEHA', db)
            >>> print(f"Current EMI burden: ₹{current_emi:,.0f}/month")
        """
        query = """
            SELECT COALESCE(SUM(monthly_emi), 0) as total_emi
            FROM emi_commitments
            WHERE user_id = ?
            AND end_date >= DATE('now')
        """

        try:
            result = db_manager.execute_one(query, (user_id,))

            if result and result['total_emi']:
                total_emi = float(result['total_emi'])
                logger.info(f"User {user_id} current EMI burden: ₹{total_emi:,.0f}/month")
                return total_emi

            return 0.0

        except Exception as e:
            logger.error(f"Failed to calculate EMI burden for {user_id}: {str(e)}")
            # Return 0 on error - conservative approach (allows transaction)
            # In production, might want to reject on DB errors
            return 0.0

    @staticmethod
    def check_affordability(
        monthly_income: float,
        current_emi_burden: float,
        new_monthly_emi: float
    ) -> Dict[str, any]:
        """
        Check if user can afford new EMI without exceeding 50% income threshold.

        Implements deterministic affordability rule:
        - Total EMI (current + new) <= 50% of monthly income

        Args:
            monthly_income: User's monthly income in rupees
            current_emi_burden: Existing monthly EMI commitments
            new_monthly_emi: Proposed new monthly EMI amount

        Returns:
            {
                'is_affordable': bool,
                'total_emi_burden': float,
                'emi_to_income_ratio': float,
                'max_allowed_emi': float,
                'available_emi_capacity': float,
                'reason': str | None
            }

        Example - Affordable:
            >>> result = AffordabilityCalculator.check_affordability(
            ...     monthly_income=50000,
            ...     current_emi_burden=15000,
            ...     new_monthly_emi=5000
            ... )
            >>> assert result['is_affordable'] == True
            >>> assert result['emi_to_income_ratio'] == 0.4  # 40%

        Example - Not Affordable:
            >>> result = AffordabilityCalculator.check_affordability(
            ...     monthly_income=30000,
            ...     current_emi_burden=20000,
            ...     new_monthly_emi=5000
            ... )
            >>> assert result['is_affordable'] == False
            >>> assert result['emi_to_income_ratio'] > 0.5  # >50%
            >>> assert "exceeds 50%" in result['reason']
        """
        # Handle missing income data
        if monthly_income <= 0:
            logger.warning("Income information not available - cannot assess affordability")
            return {
                'is_affordable': False,
                'total_emi_burden': 0,
                'emi_to_income_ratio': 0,
                'max_allowed_emi': 0,
                'available_emi_capacity': 0,
                'reason': 'Income information not available. Please update your profile to use Pay Later.'
            }

        # Calculate total EMI burden
        total_emi = current_emi_burden + new_monthly_emi

        # Calculate EMI-to-income ratio
        emi_ratio = total_emi / monthly_income

        # Calculate maximum allowed EMI (50% of income)
        max_allowed = monthly_income * AffordabilityCalculator.MAX_EMI_TO_INCOME_RATIO

        # Determine affordability
        is_affordable = total_emi <= max_allowed

        # Generate reason for rejection if not affordable
        reason = None
        if not is_affordable:
            exceeds_by = total_emi - max_allowed
            reason = (
                f"Total monthly EMI of ₹{total_emi:,.0f} would exceed 50% of your "
                f"₹{monthly_income:,.0f} monthly income. "
                f"Maximum allowed EMI: ₹{max_allowed:,.0f}. "
                f"You're over by ₹{exceeds_by:,.0f}. "
                f"For your financial safety, please choose a smaller purchase amount "
                f"or pay using UPI, Card, or Netbanking."
            )

            logger.warning(
                f"Affordability check failed: income=₹{monthly_income:,.0f}, "
                f"current_emi=₹{current_emi_burden:,.0f}, "
                f"new_emi=₹{new_monthly_emi:,.0f}, "
                f"total_emi=₹{total_emi:,.0f} ({emi_ratio*100:.1f}% of income)"
            )
        else:
            logger.info(
                f"Affordability check passed: total_emi=₹{total_emi:,.0f} "
                f"({emi_ratio*100:.1f}% of ₹{monthly_income:,.0f} income)"
            )

        return {
            'is_affordable': is_affordable,
            'total_emi_burden': round(total_emi, 2),
            'emi_to_income_ratio': round(emi_ratio, 4),
            'max_allowed_emi': round(max_allowed, 2),
            'available_emi_capacity': round(max(0, max_allowed - current_emi_burden), 2),
            'reason': reason
        }

    @staticmethod
    def get_max_affordable_purchase(
        monthly_income: float,
        current_emi_burden: float,
        emi_duration_months: int,
        annual_interest_rate: float = 12.0
    ) -> float:
        """
        Calculate maximum purchase amount user can afford given income and commitments.

        Uses reverse EMI calculation to find principal amount that results in
        monthly EMI within 50% income threshold.

        Args:
            monthly_income: User's monthly income
            current_emi_burden: Current monthly EMI commitments
            emi_duration_months: Proposed EMI tenure (e.g., 6 months)
            annual_interest_rate: Annual interest rate percentage (default: 12%)

        Returns:
            Maximum affordable purchase amount (float)

        Example:
            >>> max_purchase = AffordabilityCalculator.get_max_affordable_purchase(
            ...     monthly_income=50000,
            ...     current_emi_burden=15000,
            ...     emi_duration_months=6,
            ...     annual_interest_rate=12.0
            ... )
            >>> print(f"You can afford up to ₹{max_purchase:,.0f}")
        """
        if monthly_income <= 0:
            return 0.0

        # Calculate available EMI capacity
        max_allowed_emi = monthly_income * AffordabilityCalculator.MAX_EMI_TO_INCOME_RATIO
        available_emi = max(0, max_allowed_emi - current_emi_burden)

        if available_emi <= 0:
            return 0.0

        # Reverse EMI calculation: find principal for given monthly EMI
        # EMI = P * r * (1+r)^n / ((1+r)^n - 1)
        # Rearrange: P = EMI * ((1+r)^n - 1) / (r * (1+r)^n)

        monthly_rate = annual_interest_rate / 12 / 100

        if monthly_rate == 0:
            # No cost EMI
            max_principal = available_emi * emi_duration_months
        else:
            rate_multiplier = pow(1 + monthly_rate, emi_duration_months)
            max_principal = available_emi * (rate_multiplier - 1) / (monthly_rate * rate_multiplier)

        logger.info(
            f"Max affordable purchase: ₹{max_principal:,.0f} "
            f"(income=₹{monthly_income:,.0f}, available_emi=₹{available_emi:,.0f}, "
            f"tenure={emi_duration_months} months)"
        )

        return round(max_principal, 2)
