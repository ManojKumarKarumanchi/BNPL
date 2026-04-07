# GrabOn BNPL MCP Server

FastMCP-based server exposing credit scoring tools to Claude.

## Overview

This MCP server implements a **6-factor credit scoring model** for GrabOn's BNPL system:

1. **Purchase Frequency** (30%) - Transactions per month
2. **Return Behavior** (25%) - Inverse of return rate (>10% = rejection)
3. **GMV Trajectory** (20%) - Spending trend over time
4. **Category Diversity** (10%) - Unique categories (1-6)
5. **Coupon Redemption** (10%) - Quality signal
6. **Fraud Check** (5%) - New users (<7 days) blocked

## Installation

```bash
cd mcp-server
pip install -r requirements.txt
```

## Configuration

Create `.env` file:

```bash
# Required
ANTHROPIC_API_KEY=your_claude_api_key_here

# Optional
DATABASE_PATH=../synthetic-data-gen/output/grabon_bnpl.db
```

## Usage

### Start MCP Server

```bash
python server.py
```

### Available Tools

#### 1. get_user_profile_tool

Fetch user data and transaction history.

```python
{
  "user_id": "USR_SNEHA"
}
```

**Returns:**
```json
{
  "user_id": "USR_SNEHA",
  "name": "Sneha Reddy",
  "total_purchases": 48,
  "avg_order_value": 2850,
  "return_rate": 0.02,
  "categories": ["Electronics", "Fashion", "Beauty"],
  "transactions": [...]
}
```

#### 2. calculate_credit_score_tool

Apply 6-factor scoring model.

```python
{
  "user_id": "USR_SNEHA",
  "purchase_amount": 12499
}
```

**Returns:**
```json
{
  "credit_tier": "regular",
  "credit_limit": 25000,
  "decision": "approved",
  "total_score": 78.5,
  "score_breakdown": {
    "purchase_frequency": 80,
    "return_behavior": 90,
    "gmv_trajectory": 65,
    "category_diversity": 83,
    "coupon_redemption": 92,
    "fraud_check": 100
  }
}
```

#### 3. generate_emi_options_tool

Create EMI plans.

```python
{
  "credit_tier": "regular",
  "purchase_amount": 12499,
  "credit_limit": 25000
}
```

**Returns:**
```json
{
  "emi_options": [
    {"id": 1, "duration": 3, "monthly_payment": 4166, "tag": "No Cost EMI", "interest_rate": 0},
    {"id": 2, "duration": 6, "monthly_payment": 2150, "tag": "Best Value", "interest_rate": 3.2},
    {"id": 3, "duration": 9, "monthly_payment": 1500, "tag": null, "interest_rate": 8}
  ]
}
```

#### 4. explain_credit_decision_tool

Generate AI narrative using Claude API.

```python
{
  "user_id": "USR_SNEHA",
  "credit_score_result": {...},
  "user_profile": {...}
}
```

**Returns:**
```json
{
  "reason": "Based on your frequent purchases, low return rate of 2%, and consistent spending over the past 6 months, you've been pre-approved for instant credit."
}
```

#### 5. health_check

Check server health.

**Returns:**
```json
{
  "status": "healthy",
  "database": "connected",
  "users": 5
}
```

## Credit Tiers

| Tier     | Limit      | EMI Options    | Criteria                    |
|----------|------------|----------------|-----------------------------|
| new_user | ₹0         | None           | <7 days membership          |
| risky    | ₹0         | None           | >10% return rate            |
| growing  | ₹15,000    | 3, 6 months    | Score ≥55, 10+ transactions |
| regular  | ₹25,000    | 3, 6, 9 months | Score ≥70, 30+ transactions |
| power    | ₹50,000    | 3, 6, 9, 12 mo | Score ≥85, 100+ transactions|

## Testing

### Test with Vikram (Power User)

```bash
# Expected: ₹50K limit, 4 EMI options, 0% returns
python -c "
from tools.calculate_credit_score import calculate_credit_score
result = calculate_credit_score('USR_VIKRAM', 12499)
print(f\"Tier: {result['credit_tier']}\")
print(f\"Limit: ₹{result['credit_limit']:,}\")
print(f\"Score: {result['total_score']}\")
"
```

### Test with Priya (Risky User)

```bash
# Expected: Rejection due to 18% return rate
python -c "
from tools.calculate_credit_score import calculate_credit_score
result = calculate_credit_score('USR_PRIYA', 12499)
print(f\"Decision: {result['decision']}\")
print(f\"Reason: {result.get('rejection_reason', 'N/A')}\")
"
```

## Architecture

```
MCP Server
├── server.py (FastMCP)
├── tools/ (4 MCP tools)
│   ├── get_user_profile.py
│   ├── calculate_credit_score.py
│   ├── generate_emi_options.py
│   └── explain_credit_decision.py
├── utils/
│   ├── scoring_engine.py (6-factor model)
│   ├── emi_calculator.py
│   └── claude_client.py
├── db/
│   └── manager.py (Singleton DB manager)
└── prompts/
    └── credit_narrative.py
```

## Integration with FastAPI

The MCP server can be called from FastAPI via HTTP client:

```python
# In FastAPI route
from services.mcp_client import MCPClient

mcp = MCPClient("http://localhost:8001")
result = await mcp.call_tool("calculate_credit_score_tool", {
    "user_id": "USR_SNEHA",
    "purchase_amount": 12499
})
```

## Next Steps

1. Start MCP server: `python server.py`
2. Test tools with sample users
3. Proceed to FastAPI integration (Phase 3)
