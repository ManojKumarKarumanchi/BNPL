"""Pydantic models for MCP tool inputs and outputs."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TransactionHistory(BaseModel):
    """User transaction history summary."""
    total_purchases: int = Field(..., description="Total number of completed purchases")
    avg_order_value: float = Field(..., description="Average order value in rupees")
    return_rate: float = Field(..., description="Return rate as decimal (0-1)")
    member_since: str = Field(..., description="User registration date (YYYY-MM-DD)")
    categories: List[str] = Field(default_factory=list, description="Unique shopping categories")


class UserProfileResponse(BaseModel):
    """User profile with transaction history."""
    user_id: str = Field(..., description="User identifier (e.g., USR_AMIT)")
    name: str = Field(default="", description="User's full name")
    email: str = Field(default="", description="User's email address")
    member_since: str = Field(default="", description="Registration date (YYYY-MM-DD)")
    total_purchases: int = Field(default=0, description="Total completed purchases")
    avg_order_value: float = Field(default=0.0, description="Average order value in rupees")
    return_rate: float = Field(default=0.0, description="Return rate as decimal (0-1)")
    categories: List[str] = Field(default_factory=list, description="Shopping categories")
    transactions: List[Dict[str, Any]] = Field(default_factory=list, description="Recent transactions")
    error: Optional[str] = Field(None, description="Error message if any")


class ScoreBreakdown(BaseModel):
    """Detailed score breakdown by factor."""
    purchase_frequency: float = Field(..., description="Purchase frequency score (0-100)")
    return_behavior: float = Field(..., description="Return behavior score (0-100)")
    gmv_trajectory: float = Field(..., description="GMV trajectory score (0-100)")
    category_diversity: float = Field(..., description="Category diversity score (0-100)")
    coupon_redemption: float = Field(..., description="Coupon redemption score (0-100)")
    fraud_check: float = Field(..., description="Fraud check score (0-100)")


class CreditScoreResponse(BaseModel):
    """Credit scoring result."""
    user_id: str = Field(..., description="User identifier")
    total_score: float = Field(default=0.0, description="Total credit score (0-100)")
    credit_tier: str = Field(..., description="Credit tier: new_user, risky, growing, regular, power")
    credit_limit: float = Field(..., description="Approved credit limit in rupees")
    decision: str = Field(..., description="Decision: approved, not_eligible, new_user, amount_exceeds_limit")
    rejection_reason: Optional[str] = Field(None, description="Reason if rejected")
    purchase_amount: float = Field(default=0.0, description="Purchase amount for this transaction")
    score_breakdown: ScoreBreakdown = Field(..., description="Detailed score breakdown")
    min_transactions: int = Field(default=10, description="Minimum transactions required for approval")
    error: Optional[str] = Field(None, description="Error message if any")


class EMIOption(BaseModel):
    """Single EMI option."""
    id: int = Field(..., description="Option ID")
    duration: int = Field(..., description="Duration in months")
    monthly_payment: float = Field(..., description="Monthly payment amount in rupees")
    tag: Optional[str] = Field(None, description="Tag like 'No Cost EMI', 'Best Value', 'VIP Rate'")
    total_amount: float = Field(..., description="Total amount to be paid")
    interest_rate: float = Field(..., description="Interest rate percentage")
    processing_fee: float = Field(default=0.0, description="Processing fee in rupees")
    provider: Optional[str] = Field(None, description="EMI provider name")


class EMIOptionsResponse(BaseModel):
    """EMI options for a purchase."""
    emi_options: List[EMIOption] = Field(default_factory=list, description="Available EMI plans")
    credit_tier: str = Field(default="", description="User's credit tier")
    credit_limit: float = Field(default=0.0, description="User's credit limit in rupees")
    purchase_amount: float = Field(default=0.0, description="Purchase amount in rupees")
    error: Optional[str] = Field(None, description="Error message if any")


class CreditNarrativeResponse(BaseModel):
    """AI-generated credit decision narrative."""
    user_id: str = Field(..., description="User identifier")
    reason: str = Field(..., description="Plain-language explanation of credit decision")
    status: str = Field(default="approved", description="Decision status: approved, not_eligible, new_user")
    error: Optional[str] = Field(None, description="Error message if any")


class HealthCheckResponse(BaseModel):
    """MCP server health status."""
    status: str = Field(..., description="Health status: healthy or unhealthy")
    database: str = Field(default="unknown", description="Database connection status: connected or disconnected")
    users: int = Field(default=0, description="Total users in database")
    transactions: int = Field(default=0, description="Total transactions in database")
    server: str = Field(..., description="MCP server name")
    version: str = Field(..., description="MCP server version")
    error: Optional[str] = Field(None, description="Error message if unhealthy")
