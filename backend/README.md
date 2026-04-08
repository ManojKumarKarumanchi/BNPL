# GrabCredit BNPL Backend

Complete backend implementation for GrabOn's BNPL credit scoring system.

## Overview

The backend consists of three modules:

1. **Synthetic Data Generation** - Creates realistic transaction data for 5 user personas
2. **MCP Server** - Exposes credit scoring tools to Claude AI
3. **FastAPI REST API** - Production REST endpoints for frontend integration

---

## Quick Start

### 1. Setup Environment

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
# OR
source .venv/bin/activate      # macOS/Linux

pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `.env` file in `backend/` folder:

```env
# Database
DATABASE_PATH=./synthetic-data-gen/output/grabon_bnpl.db

# Azure OpenAI (for AI narratives)
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5.1
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# MCP Server
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=5000

# FastAPI
API_HOST=localhost
API_PORT=8000
ENVIRONMENT=development
```

### 3. Generate Synthetic Data

```bash
cd synthetic-data-gen
python main.py
```

**Output:**
- Creates `output/grabon_bnpl.db` (SQLite database)
- Generates 5 users (Rajesh, Priya, Amit, Sneha, Vikram)
- Creates ~318 transactions with realistic patterns

### 4. Start Backend Server

```bash
cd backend
python run.py
```

**Server runs on:** http://localhost:8000

**Verify:**
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","mcp_server":"connected"}
```

---

## Module Details

### 1. Synthetic Data Generation (`synthetic-data-gen/`)

Generates realistic transaction data using Evidently AI and Faker.

**Key Files:**
- `main.py` - Entry point for data generation
- `config.py` - 5 persona configurations (matches frontend personas)
- `generators/transaction_generator.py` - Transaction generation logic
- `generators/user_generator.py` - User profile generation
- `output/grabon_bnpl.db` - Generated SQLite database

**Persona Data:**

| User ID | Name | Transactions | Avg Order | Return Rate | Member Since | Credit Tier |
|---------|------|--------------|-----------|-------------|--------------|-------------|
| USR_RAJESH | Rajesh Kumar | 0 | ₹0 | 0% | 2026-04-01 | New User |
| USR_PRIYA | Priya Sharma | 8 | ₹950 | 0% | 2025-12-10 | Risky |
| USR_AMIT | Amit Patel | 25 | ₹1,850 | 0% | 2025-12-01 | Growing |
| USR_SNEHA | Sneha Reddy | 48 | ₹2,850 | 2% | 2024-08-15 | Regular |
| USR_VIKRAM | Vikram Singh | 237 | ₹4,200 | 0% | 2024-10-15 | Power |

**Database Schema:**

```sql
-- Users table
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    member_since DATE NOT NULL,
    account_status TEXT DEFAULT 'active'
);

-- Transactions table
CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    merchant_id TEXT NOT NULL,
    category TEXT NOT NULL,
    order_value REAL NOT NULL,
    discount_amount REAL DEFAULT 0,
    final_amount REAL NOT NULL,
    coupon_used TEXT,
    payment_mode TEXT,
    is_returned BOOLEAN DEFAULT 0,
    transaction_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Merchants table
CREATE TABLE merchants (
    merchant_id TEXT PRIMARY KEY,
    merchant_name TEXT NOT NULL,
    avg_discount_percent REAL,
    deal_count INTEGER DEFAULT 0
);
```

---

### 2. MCP Server (`mcp-server/`)

FastMCP server exposing 5 tools for credit scoring and eligibility checks.

**Run MCP Server:**
```bash
cd mcp-server
python server.py
```

**Available Tools:**

1. **get_user_profile** - Fetch user profile and transaction summary
   ```python
   Input: user_id (str)
   Output: {name, email, member_since, total_purchases, avg_order_value, return_rate}
   ```

2. **calculate_credit_score** - 6-factor credit scoring algorithm
   ```python
   Input: user_id (str), purchase_amount (float)
   Output: {total_score, credit_tier, credit_limit, score_breakdown}
   ```

3. **generate_emi_options** - Generate EMI plans based on credit tier
   ```python
   Input: credit_tier (str), purchase_amount (float), credit_limit (float)
   Output: [{id, duration, monthly_payment, total_amount, interest_rate, tag}]
   ```

4. **explain_credit_decision** - AI-generated human-readable narrative
   ```python
   Input: user_id (str), credit_score_result (dict), user_profile (dict)
   Output: personalized credit decision explanation (via Azure OpenAI)
   ```

5. **get_user_transactions** - Fetch full transaction history
   ```python
   Input: user_id (str), limit (int, optional)
   Output: [{transaction_id, merchant, category, amount, date, is_returned}]
   ```

**Credit Scoring Algorithm (6 Factors):**

```python
# 1. Purchase Frequency (30%)
purchase_frequency_score = min(txns_per_month * 10, 100)

# 2. Return Behavior (25%)
return_behavior_score = 100 - (return_rate * 10)  # >10% = auto-reject

# 3. GMV Trajectory (20%)
gmv_trajectory_score = linear_regression_slope(monthly_gmv) * 100

# 4. Category Diversity (10%)
category_diversity_score = (unique_categories / 6) * 100

# 5. Coupon Redemption (10%)
coupon_redemption_score = (coupon_usage_rate) * 100

# 6. Fraud Check (5%)
fraud_check_score = 100 if days_since_joined >= 7 else 0  # <7 days = auto-block

# Total Score
total_score = (
    purchase_frequency_score * 0.30 +
    return_behavior_score * 0.25 +
    gmv_trajectory_score * 0.20 +
    category_diversity_score * 0.10 +
    coupon_redemption_score * 0.10 +
    fraud_check_score * 0.05
)
```

**Credit Tiers:**

| Score Range | Tier | Credit Limit | EMI Options |
|-------------|------|--------------|-------------|
| < 40 | New User | ₹0 | None |
| 40-55 | Risky | ₹0 | None |
| 56-70 | Growing | ₹15,000 | 3/6 months |
| 71-85 | Regular | ₹25,000 | 3/6/9 months |
| 86-100 | Power | ₹50,000 | 3/6/9/12 months |

---

### 3. FastAPI REST API (`api/`)

Production REST endpoints for frontend integration.

**Run API Server:**
```bash
cd backend
python run.py
```

**Endpoints:**

#### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "mcp_server": "connected"
}
```

#### Check BNPL Eligibility
```bash
POST /api/checkout/eligibility
Content-Type: application/json

Request:
{
  "user_id": "USR_SNEHA",
  "product_id": "PROD_001",
  "amount": 12499
}

Response:
{
  "status": "approved",
  "credit_limit": 15000.0,
  "reason": "Great news! You've been approved for ₹15,000 credit...",
  "transaction_history": {
    "total_purchases": 48,
    "avg_order_value": 2850,
    "return_rate": 2.0,
    "member_since": "2024-08-15"
  },
  "emi_options": [
    {
      "id": 1,
      "duration": 3,
      "monthly_payment": 4166.33,
      "tag": "No Cost EMI",
      "total_amount": 12498.99,
      "interest_rate": 0.0
    }
  ],
  "score_details": {
    "purchase_frequency": 58.59,
    "return_behavior": 100.0,
    "gmv_trajectory": 55.05,
    "category_diversity": 66.68,
    "coupon_redemption": 92.0,
    "fraud_check": 100
  }
}
```

**Middleware:**
- **CORS** - Allows frontend (localhost:5173) to access API
- **Rate Limiting** - 60 req/min, 500 req/hour per user (via Redis)
- **Error Handling** - Structured error responses
- **Session Management** - JWT tokens (24-hour TTL)

---

## Testing

### Test Individual MCP Tools

```bash
# Start MCP server first
cd mcp-server
python server.py

# In another terminal, use the MCP client
python -c "
from tools.get_user_profile import get_user_profile
print(get_user_profile('USR_SNEHA'))
"
```

### Test API Endpoints

```bash
# Test all 5 personas
for user in USR_RAJESH USR_PRIYA USR_AMIT USR_SNEHA USR_VIKRAM; do
  echo "Testing $user..."
  curl -s -X POST http://localhost:8000/api/checkout/eligibility \
    -H "Content-Type: application/json" \
    -d "{\"user_id\":\"$user\",\"product_id\":\"PROD_001\",\"amount\":12499}" \
    | python -m json.tool
  echo "---"
done
```

### Expected Results

✅ **USR_RAJESH**: `status: "not_eligible"` (new user <7 days)  
✅ **USR_PRIYA**: `status: "approved"`, `credit_limit: 15000`  
✅ **USR_AMIT**: `status: "approved"`, `credit_limit: 15000`  
✅ **USR_SNEHA**: `status: "approved"`, `credit_limit: 15000`  
✅ **USR_VIKRAM**: `status: "approved"`, `credit_limit: 50000`

---

## Dependencies

All dependencies are managed in a single `requirements.txt` file:

```
fastapi==0.115.0
uvicorn[standard]==0.32.0
fastmcp==1.2.0
mcp==1.26.0
openai==1.59.8
httpx==0.28.1
sqlalchemy==2.0.36
pandas==2.2.3
numpy==2.2.2
evidently==0.7.21
faker==33.1.0
pydantic==2.10.4
pydantic-settings==2.7.0
python-dotenv==1.0.1
python-multipart==0.0.20
```

**Install:**
```bash
pip install -r requirements.txt
```

---

## Troubleshooting

### Database not found
```bash
cd synthetic-data-gen
python main.py  # Regenerate database
```

### MCP server won't start
Check database path in `.env`:
```env
DATABASE_PATH=./synthetic-data-gen/output/grabon_bnpl.db
```

### Azure OpenAI errors
Check Azure OpenAI credentials in `.env`:
```env
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_KEY=your-api-key-here
```

If Azure OpenAI is not configured, the system falls back to generic narratives.

### Port already in use
Kill existing processes:
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

---

## Architecture

```
Frontend (React)
    ↓
    POST /api/checkout/eligibility
    ↓
FastAPI Server (api/)
    ↓ (calls MCP tools via HTTP)
    ↓
MCP Server (mcp-server/)
    ↓
    ├─ get_user_profile() → SQLite DB
    ├─ calculate_credit_score() → Scoring Engine
    ├─ generate_emi_options() → EMI Calculator
    └─ explain_credit_decision() → Azure OpenAI
    ↓
Response: {status, credit_limit, emi_options, reason}
```

---

## Support

For backend issues:
1. Check backend logs: `python run.py` console output
2. Verify database exists: `ls synthetic-data-gen/output/grabon_bnpl.db`
3. Test MCP tools independently
4. Check Azure OpenAI credentials
5. Verify all services are running (MCP server + FastAPI server)
