"""Response schemas for API endpoints."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TransactionHistory(BaseModel):
    """Transaction history summary."""

    total_purchases: int = Field(..., description="Total number of purchases")
    avg_order_value: float = Field(..., description="Average order value in INR")
    return_rate: float = Field(..., description="Return rate as percentage (0-100)")
    member_since: str = Field(..., description="Membership start date (YYYY-MM-DD)")


class EMIOption(BaseModel):
    """EMI plan option."""

    id: int = Field(..., description="EMI option ID")
    duration: int = Field(..., description="Duration in months")
    monthly_payment: float = Field(..., description="Monthly payment amount in INR")
    tag: Optional[str] = Field(None, description="EMI tag (e.g., 'No Cost EMI', 'Best Value')")
    total_amount: float = Field(..., description="Total amount to be paid")
    interest_rate: float = Field(..., description="Annual interest rate (%)")
    processing_fee: Optional[float] = Field(0, description="Processing fee (if any)")
    provider: Optional[str] = Field(None, description="EMI provider (e.g., 'PayU LazyPay')")


class EligibilityResponse(BaseModel):
    """Response schema for checkout eligibility."""

    status: str = Field(
        ...,
        description="Eligibility status: 'approved', 'not_eligible', or 'new_user'",
        examples=["approved"]
    )

    credit_limit: float = Field(
        ...,
        description="Credit limit in INR",
        examples=[25000.0]
    )

    reason: str = Field(
        ...,
        description="AI-generated personalized explanation",
        examples=["Based on your frequent purchases, low return rate of 2%, and consistent spending over the past 6 months, you've been pre-approved for instant credit."]
    )

    transaction_history: TransactionHistory = Field(
        ...,
        description="User's transaction history summary"
    )

    emi_options: Optional[List[EMIOption]] = Field(
        None,
        description="Available EMI options (null if not approved)"
    )

    payu_transaction_id: Optional[str] = Field(
        None,
        description="PayU transaction ID (if PayU API was used)"
    )

    emi_provider: Optional[str] = Field(
        "GrabCredit",
        description="EMI provider name (PayU LazyPay or local)"
    )

    score_details: Optional[Dict[str, Any]] = Field(
        None,
        description="Credit score breakdown (optional, for debugging)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "approved",
                "credit_limit": 25000.0,
                "reason": "Based on your frequent purchases, low return rate of 2%, and consistent spending over the past 6 months, you've been pre-approved for instant credit.",
                "transaction_history": {
                    "total_purchases": 48,
                    "avg_order_value": 2850.0,
                    "return_rate": 2.0,
                    "member_since": "2024-08-15"
                },
                "emi_options": [
                    {
                        "id": 1,
                        "duration": 3,
                        "monthly_payment": 4166.33,
                        "tag": "No Cost EMI",
                        "total_amount": 12499.0,
                        "interest_rate": 0.0
                    },
                    {
                        "id": 2,
                        "duration": 6,
                        "monthly_payment": 2150.0,
                        "tag": "Best Value",
                        "total_amount": 12900.0,
                        "interest_rate": 3.2
                    }
                ]
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    mcp_server: str = Field(..., description="MCP server connection status")


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")
