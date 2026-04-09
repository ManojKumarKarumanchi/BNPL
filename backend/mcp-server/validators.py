"""Input validation for MCP tools."""

import re
from typing import Optional


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


def validate_user_id(user_id: str) -> None:
    """
    Validate user_id format.

    Args:
        user_id: User identifier to validate

    Raises:
        ValidationError: If user_id is invalid
    """
    if not user_id:
        raise ValidationError("user_id is required")

    if not isinstance(user_id, str):
        raise ValidationError("user_id must be a string")

    # Must match pattern USR_<uppercase letters>
    if not re.match(r'^USR_[A-Z]+$', user_id):
        raise ValidationError(
            f"user_id must match pattern 'USR_<NAME>' (e.g., 'USR_AMIT'), got: {user_id}"
        )


def validate_credit_tier(tier: str) -> None:
    """
    Validate credit tier value.

    Args:
        tier: Credit tier to validate

    Raises:
        ValidationError: If tier is invalid
    """
    valid_tiers = {'new_user', 'risky', 'growing', 'regular', 'power'}

    if tier not in valid_tiers:
        raise ValidationError(
            f"credit_tier must be one of {valid_tiers}, got: {tier}"
        )


def validate_amount(amount: float, name: str = "amount", min_value: float = 0) -> None:
    """
    Validate monetary amount.

    Args:
        amount: Amount to validate
        name: Name of the field (for error messages)
        min_value: Minimum allowed value

    Raises:
        ValidationError: If amount is invalid
    """
    if not isinstance(amount, (int, float)):
        raise ValidationError(f"{name} must be a number, got: {type(amount)}")

    if amount < min_value:
        raise ValidationError(f"{name} must be >= {min_value}, got: {amount}")

    # Reasonable upper limit for Indian e-commerce (1 crore)
    if amount > 10_000_000:
        raise ValidationError(f"{name} seems unreasonably high: ₹{amount:,.0f}")


def validate_purchase_amount(amount: float) -> None:
    """Validate purchase amount specifically."""
    validate_amount(amount, "purchase_amount", min_value=1)


def validate_credit_limit(limit: float) -> None:
    """Validate credit limit specifically."""
    validate_amount(limit, "credit_limit", min_value=0)

    # Credit limit tiers
    valid_limits = {0, 15000, 25000, 50000}
    if limit not in valid_limits:
        raise ValidationError(
            f"credit_limit must be one of {valid_limits}, got: {limit}"
        )
