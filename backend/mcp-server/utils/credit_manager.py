"""
Credit Manager - Atomic credit utilization tracking.

Prevents race conditions and credit limit exceedance through:
1. Atomic queries with database transactions
2. Outstanding balance tracking
3. Real-time credit availability calculation
4. Credit reservation for purchases
"""

from db.manager import get_db
import uuid
from typing import Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CreditManager:
    """Manages credit limit utilization with atomic operations."""

    @staticmethod
    def get_available_credit(user_id: str, credit_limit: float) -> Dict[str, float]:
        """
        Calculate available credit with thread-safe query.

        Performs atomic read of user's outstanding credit utilization to prevent
        race conditions where multiple requests could exceed credit limit.

        Args:
            user_id: User identifier
            credit_limit: User's approved credit limit

        Returns:
            {
                'credit_limit': float,
                'utilized_amount': float,
                'outstanding_dues': float,
                'available_credit': float
            }

        Example:
            >>> credit_status = CreditManager.get_available_credit('USR_SNEHA', 25000)
            >>> print(f"Available: ₹{credit_status['available_credit']:,.0f}")
            >>> if credit_status['available_credit'] < 12499:
            >>>     print("Insufficient credit")
        """
        db = get_db()

        # Get total outstanding amount (atomic read with transaction)
        query = """
            SELECT COALESCE(SUM(outstanding_amount), 0) as total_outstanding
            FROM credit_utilization
            WHERE user_id = ?
            AND status = 'active'
        """

        try:
            with db.transaction():
                result = db.execute_one(query, (user_id,))
                outstanding = float(result['total_outstanding']) if result else 0.0

            available = max(0, credit_limit - outstanding)

            logger.info(
                f"Credit availability for {user_id}: "
                f"limit=₹{credit_limit:,.0f}, "
                f"outstanding=₹{outstanding:,.0f}, "
                f"available=₹{available:,.0f}"
            )

            return {
                'credit_limit': credit_limit,
                'utilized_amount': outstanding,
                'outstanding_dues': outstanding,
                'available_credit': available
            }

        except Exception as e:
            logger.error(f"Failed to get available credit for {user_id}: {str(e)}")
            # Conservative approach: return zero available credit on error
            return {
                'credit_limit': credit_limit,
                'utilized_amount': 0,
                'outstanding_dues': 0,
                'available_credit': 0,
                'error': str(e)
            }

    @staticmethod
    def reserve_credit(
        user_id: str,
        purchase_amount: float,
        credit_limit: float
    ) -> Dict[str, any]:
        """
        Atomically reserve credit for purchase.

        Uses database transactions to ensure that credit limit is not exceeded
        even with concurrent requests. This prevents the race condition where:
        - User A and User B both check available credit (both see ₹15K available)
        - Both submit ₹12K purchases
        - Total utilization = ₹24K (exceeds ₹15K limit)

        SQLite Note: Uses BEGIN IMMEDIATE to lock database for writes.
        PostgreSQL: Would use SELECT ... FOR UPDATE for row-level locking.

        Args:
            user_id: User identifier
            purchase_amount: Amount to reserve
            credit_limit: User's credit limit

        Returns:
            {
                'success': bool,
                'purchase_id': str | None,
                'available_credit': float,
                'error': str | None
            }

        Example - Success:
            >>> result = CreditManager.reserve_credit('USR_SNEHA', 12499, 25000)
            >>> if result['success']:
            >>>     print(f"Reserved ₹12,499. Purchase ID: {result['purchase_id']}")

        Example - Failure (Insufficient Credit):
            >>> result = CreditManager.reserve_credit('USR_AMIT', 18000, 15000)
            >>> if not result['success']:
            >>>     print(result['error'])  # "Insufficient credit..."
        """
        db = get_db()

        try:
            with db.transaction():
                # SQLite: BEGIN IMMEDIATE provides write lock
                # This prevents other transactions from starting until we commit/rollback

                # Get current outstanding (within transaction - locked)
                result = db.execute_one(
                    """
                    SELECT COALESCE(SUM(outstanding_amount), 0) as total
                    FROM credit_utilization
                    WHERE user_id = ?
                    AND status = 'active'
                    """,
                    (user_id,)
                )

                current_outstanding = float(result['total']) if result else 0.0
                available = credit_limit - current_outstanding

                # Check if purchase amount exceeds available credit
                if purchase_amount > available:
                    logger.warning(
                        f"Insufficient credit for {user_id}: "
                        f"requested=₹{purchase_amount:,.0f}, "
                        f"available=₹{available:,.0f}"
                    )

                    return {
                        'success': False,
                        'purchase_id': None,
                        'available_credit': available,
                        'error': (
                            f"Insufficient credit. You have ₹{current_outstanding:,.0f} outstanding dues. "
                            f"Available credit: ₹{available:,.0f}. "
                            f"Requested: ₹{purchase_amount:,.0f}. "
                            f"Please pay your dues or choose a smaller amount."
                        )
                    }

                # Reserve credit (insert into utilization table)
                purchase_id = f"PUR_{uuid.uuid4().hex[:12].upper()}"

                db.connection.execute(
                    """
                    INSERT INTO credit_utilization
                    (user_id, purchase_id, purchase_amount, outstanding_amount, status, created_at)
                    VALUES (?, ?, ?, ?, 'active', ?)
                    """,
                    (user_id, purchase_id, purchase_amount, purchase_amount, datetime.now().isoformat())
                )

                new_available = available - purchase_amount

                logger.info(
                    f"Credit reserved for {user_id}: "
                    f"purchase_id={purchase_id}, "
                    f"amount=₹{purchase_amount:,.0f}, "
                    f"new_available=₹{new_available:,.0f}"
                )

                # Transaction commits here (automatic with context manager)

                return {
                    'success': True,
                    'purchase_id': purchase_id,
                    'available_credit': new_available,
                    'error': None
                }

        except Exception as e:
            logger.exception(f"Credit reservation failed for {user_id}: {str(e)}")
            return {
                'success': False,
                'purchase_id': None,
                'available_credit': 0,
                'error': f"Credit reservation failed: {str(e)}"
            }

    @staticmethod
    def release_credit(user_id: str, purchase_id: str, reason: str = "cancelled") -> bool:
        """
        Release reserved credit (e.g., if payment fails or order cancelled).

        Args:
            user_id: User identifier
            purchase_id: Purchase ID to release
            reason: Reason for release (logged)

        Returns:
            True if successful, False otherwise

        Example:
            >>> success = CreditManager.release_credit('USR_SNEHA', 'PUR_ABC123', 'payment_failed')
            >>> if success:
            >>>     print("Credit released - user can try again")
        """
        db = get_db()

        try:
            with db.transaction():
                # Update status to cancelled/released
                db.connection.execute(
                    """
                    UPDATE credit_utilization
                    SET status = 'cancelled',
                        outstanding_amount = 0
                    WHERE user_id = ?
                    AND purchase_id = ?
                    AND status = 'active'
                    """,
                    (user_id, purchase_id)
                )

                logger.info(
                    f"Credit released for {user_id}: "
                    f"purchase_id={purchase_id}, reason={reason}"
                )

                return True

        except Exception as e:
            logger.error(f"Failed to release credit for {user_id}, purchase {purchase_id}: {str(e)}")
            return False

    @staticmethod
    def mark_paid(user_id: str, purchase_id: str) -> bool:
        """
        Mark purchase as paid (clears outstanding amount).

        Args:
            user_id: User identifier
            purchase_id: Purchase ID to mark as paid

        Returns:
            True if successful, False otherwise

        Example:
            >>> # After user completes final EMI payment
            >>> success = CreditManager.mark_paid('USR_SNEHA', 'PUR_ABC123')
        """
        db = get_db()

        try:
            with db.transaction():
                db.connection.execute(
                    """
                    UPDATE credit_utilization
                    SET status = 'paid',
                        outstanding_amount = 0,
                        paid_at = ?
                    WHERE user_id = ?
                    AND purchase_id = ?
                    AND status = 'active'
                    """,
                    (datetime.now().isoformat(), user_id, purchase_id)
                )

                logger.info(
                    f"Purchase marked as paid: user={user_id}, purchase_id={purchase_id}"
                )

                return True

        except Exception as e:
            logger.error(f"Failed to mark purchase as paid for {user_id}, purchase {purchase_id}: {str(e)}")
            return False
