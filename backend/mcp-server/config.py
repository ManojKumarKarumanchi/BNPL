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

# AI Provider Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "claude")  # Options: "claude", "azure"

# Claude API configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")

# Azure OpenAI configuration
AZURE_AI_PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "")
AZURE_AI_MODEL_DEPLOYMENT_NAME = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4")
AZURE_API_KEY = os.getenv("AZURE_API_KEY", "")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "2025-04-01-preview")

# MCP Server configuration
MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "grabon-bnpl-mcp")
MCP_SERVER_VERSION = os.getenv("MCP_SERVER_VERSION", "1.0.0")
MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8001"))

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

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/mcp-server.log")
