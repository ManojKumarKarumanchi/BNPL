"""
MCP Tool: Get User Profile
Fetches user data and transaction history from database.
"""

from datetime import datetime
from typing import Dict, List, Any
from db.manager import get_db
from models import UserProfileResponse


def get_user_profile(user_id: str) -> UserProfileResponse:
    """
    Fetch user profile and transaction history.

    Args:
        user_id: User ID (e.g., "USR_SNEHA")

    Returns:
        UserProfileResponse with transaction history and error field if failed
    """
    db = get_db()

    try:
        # Fetch user data
        user = db.execute_one(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )

        if not user:
            return UserProfileResponse(
                user_id=user_id,
                error=f"User not found: {user_id}"
            )

        # Fetch all transactions for user
        transactions = db.execute_query(
            """
            SELECT
                transaction_id,
                merchant_id,
                category,
                order_value,
                discount_amount,
                final_amount,
                coupon_used,
                payment_mode,
                is_returned,
                transaction_date
            FROM transactions
            WHERE user_id = ?
            ORDER BY transaction_date DESC
            """,
            (user_id,)
        )

        # Convert to dict list
        transactions_list = [dict(txn) for txn in transactions]

        # Calculate aggregate metrics
        total_purchases = len(transactions_list)
        avg_order_value = (
            sum(txn["final_amount"] for txn in transactions_list) / total_purchases
            if total_purchases > 0 else 0
        )
        return_rate = (
            sum(1 for txn in transactions_list if txn["is_returned"]) / total_purchases
            if total_purchases > 0 else 0
        )
        unique_categories = list(set(txn["category"] for txn in transactions_list))

        return UserProfileResponse(
            user_id=user["user_id"],
            name=user["name"],
            email=user["email"],
            member_since=user["member_since"],
            total_purchases=total_purchases,
            avg_order_value=round(avg_order_value, 2),
            return_rate=round(return_rate, 4),
            categories=unique_categories,
            transactions=transactions_list,
            error=None
        )

    except Exception as e:
        return UserProfileResponse(
            user_id=user_id,
            error=f"Database error: {str(e)}"
        )
