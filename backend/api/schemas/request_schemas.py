"""Request schemas for API endpoints."""

from pydantic import BaseModel, Field, field_validator


class EligibilityRequest(BaseModel):
    """Request schema for checkout eligibility check."""

    user_id: str = Field(
        ...,
        description="User ID (e.g., USR_SNEHA)",
        min_length=3,
        max_length=50,
        examples=["USR_SNEHA"]
    )

    product_id: str = Field(
        ...,
        description="Product ID",
        min_length=3,
        max_length=100,
        examples=["PROD_SAMSUNG_WATCH"]
    )

    amount: float = Field(
        ...,
        description="Purchase amount in INR",
        gt=0,
        le=100000,
        examples=[12499.0]
    )

    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Validate user_id format."""
        if not v.startswith('USR_'):
            raise ValueError('user_id must start with USR_')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "USR_SNEHA",
                "product_id": "PROD_SAMSUNG_WATCH",
                "amount": 12499.0
            }
        }
