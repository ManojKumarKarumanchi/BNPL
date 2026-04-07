"""MCP Server configuration."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database path (points to synthetic data output)
DB_PATH = os.getenv(
    "DATABASE_PATH",
    str(Path(__file__).parent.parent / "synthetic-data-gen" / "output" / "grabon_bnpl.db")
)

# Claude API configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-5"

# MCP Server configuration
MCP_SERVER_NAME = "grabon-bnpl-mcp"
MCP_SERVER_VERSION = "1.0.0"
MCP_SERVER_PORT = 8001

# Credit tier limits
CREDIT_TIERS = {
    "new_user": {
        "credit_limit": 0,
        "emi_durations": [],
        "description": "New user - build history first"
    },
    "risky": {
        "credit_limit": 0,
        "emi_durations": [],
        "description": "High risk detected"
    },
    "growing": {
        "credit_limit": 15000,
        "emi_durations": [3, 6],
        "description": "Growing trust"
    },
    "regular": {
        "credit_limit": 25000,
        "emi_durations": [3, 6, 9],
        "description": "Regular user"
    },
    "power": {
        "credit_limit": 50000,
        "emi_durations": [3, 6, 9, 12],
        "description": "VIP status"
    }
}

# EMI interest rates by duration
EMI_INTEREST_RATES = {
    3: 0.0,    # No cost EMI
    6: 3.2,    # 3.2% annual
    9: 8.0,    # 8% annual
    12: 5.6    # 5.6% annual (VIP rate)
}

# Scoring weights (6-factor model)
SCORING_WEIGHTS = {
    "purchase_frequency": 0.30,
    "return_behavior": 0.25,
    "gmv_trajectory": 0.20,
    "category_diversity": 0.10,
    "coupon_redemption": 0.10,
    "fraud_check": 0.05
}

# Fraud detection thresholds
FRAUD_THRESHOLDS = {
    "min_days_membership": 7,     # New users blocked if <7 days
    "max_return_rate": 0.10,      # >10% return rate = rejection
    "min_transactions": 3          # Minimum txns for growing tier
}
