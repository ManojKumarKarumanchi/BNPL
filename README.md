# GrabCredit BNPL - Buy Now, Pay Later System [![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/ManojKumarKarumanchi/BNPL)

Deepwiki: https://deepwiki.com/ManojKumarKarumanchi/BNPL
Drive video link: https://acesse.one/w3hj0h5

An AI-powered credit scoring and BNPL eligibility engine for GrabOn's e-commerce platform, powered by Claude AI and Azure OpenAI.

## What I Built

GrabCredit is a **complete end-to-end BNPL system** that demonstrates production-grade credit decisioning at e-commerce checkout. The system consists of three core modules:

### 1. Synthetic Data Generation
- Generates realistic transaction data for 5 user personas (318 total transactions)
- Uses **Evidently AI datagen** + **Faker** for realistic Indian user profiles
- Produces SQLite database with users, transactions, merchants, and credit utilization tables
- Implements **50% EMI-to-income rule** (RBI guideline) with affordability calculations

### 2. MCP Server (Model Context Protocol)
- Exposes 5 tools for credit decisioning via MCP protocol
- **Synchronous architecture** with thread-local SQLite connections (singleton pattern)
- **6-factor credit scoring engine**: purchase frequency (30%), return behavior (25%), GMV trajectory (20%), category diversity (10%), coupon redemption (10%), fraud check (5%)
- Generates personalized credit narratives using **Azure OpenAI (GPT-5.1)**
- Real-time EMI options calculator with tier-based interest rates

### 3. FastAPI REST API + React Frontend
- Production-ready REST endpoint: `POST /api/checkout/eligibility`
- **Dual-mode UI**: Mock data (demo) + Real API (live database)
- Error boundaries, graceful fallbacks, and responsive design
- Real-time eligibility checking with sub-3-second latency

**Tech Stack:**
- **Backend**: FastAPI + MCP Server + Azure OpenAI (GPT-5.1)
- **Frontend**: React + TailwindCSS + Framer Motion
- **Database**: SQLite (demo) → PostgreSQL (production migration path)
- **AI**: Claude via MCP for credit scoring + Azure OpenAI for narratives

## Features

✅ **6-Factor Credit Scoring Engine**
- Purchase frequency (30%)
- Return behavior (25%)
- GMV trajectory (20%)
- Category diversity (10%)
- Coupon redemption (10%)
- Fraud velocity check (5%)

✅ **Real-time BNPL Eligibility**
- Instant credit approval/rejection
- Personalized EMI options (3/6/9/12 months)
- AI-generated human-readable credit narratives

✅ **5 User Personas (PayU LazyPay Aligned)**
- Rajesh Kumar (New User) - 0 transactions, blocked <7 days
- Priya Sharma (Risky) - 8 transactions, 18% return rate, rejected
- Amit Patel (Growing) - 25 transactions, approved ₹10K (PayU entry tier)
- Sneha Reddy (Regular) - 48 transactions, approved ₹30K (PayU standard)
- Vikram Singh (Power) - 237 transactions, approved ₹100K (PayU premium)

✅ **Production-Ready UI**
- Dual-mode: Mock data (demo) + Real API (live)
- Error boundaries & graceful fallbacks
- Responsive design with smooth animations

---

## Quick Start (5 Steps)

### Prerequisites

- **Python 3.11+** (backend)
- **Node.js 18+** (frontend)
- **Git Bash** or WSL (Windows)

### Step 1: Generate Synthetic Transaction Data

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
pip install -r ../requirements.txt

cd backend/synthetic-data-gen
python main.py
```

**Expected Output:**
```
✅ Generated 5 users (Rajesh, Priya, Amit, Sneha, Vikram)
✅ Generated 318 total transactions
✅ Database saved: backend/synthetic-data-gen/output/grabon_bnpl.db
```

---

### Step 2: Start the MCP Server

The MCP (Model Context Protocol) server exposes transaction data and credit scoring tools to Claude.

```bash
cd backend/mcp-server
source ../.venv/bin/activate  # Reuse backend venv
python server.py
```

**Expected Output:**
```
🚀 MCP Server running on http://localhost:5000
📊 Database: ../synthetic-data-gen/output/grabon_bnpl.db
🔧 Available tools: 5
```

**Keep this terminal running** - the MCP server must stay active.

---

### Step 3: Connect MCP to Claude Code/Desktop

#### Option A: Claude Code CLI

Create `.claude/mcp.json` in your project:

```json
{
  "mcpServers": {
    "grabon-bnpl": {
      "command": "python",
      "args": ["C:/Users/YourUsername/local/BNPL/backend/mcp-server/server.py"],
      "env": {
        "DATABASE_PATH": "C:/Users/YourUsername/local/BNPL/backend/synthetic-data-gen/output/grabon_bnpl.db"
      }
    }
  }
}
```

Restart Claude Code:
```bash
claude restart
```

#### Option B: Claude Desktop

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "grabon-bnpl": {
      "command": "python",
      "args": ["C:/Users/YourUsername/local/BNPL/backend/mcp-server/server.py"],
      "env": {
        "DATABASE_PATH": "C:/Users/YourUsername/local/BNPL/backend/synthetic-data-gen/output/grabon_bnpl.db"
      }
    }
  }
}
```

Restart Claude Desktop app.

**Verify MCP Connection:**
In Claude, type: `/mcp` - you should see `grabon-bnpl` with 5 tools.

---

### Step 4: Start the Backend API Server

```bash
cd backend
source .venv/Scripts/activate
python run.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://localhost:8000
INFO:     Application startup complete
✅ MCP Server connected
✅ Azure OpenAI configured
```

**Keep this terminal running.**

**Test the API:**
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","version":"1.0.0","mcp_server":"connected"}
```

---

### Step 5: Start the Frontend UI

```bash
cd frontend
npm install
npm run dev
```

**Expected Output:**
```
  VITE v6.0.1  ready in 450 ms
  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Open your browser:** http://localhost:5173

---

## How to Use the UI

### Demo Mode (Mock Data)
1. Default mode - works without backend
2. Use the **User Personas** panel on the right to switch between 5 users
3. Click "Proceed to Pay" to see EMI options

### Real API Mode (Live Database)
1. Toggle **"Use Real API"** switch (must have backend running)
2. Select a persona - data loads from SQLite database
3. EMI options generated in real-time via Azure OpenAI
4. AI narratives explain credit decisions

### Testing Personas (PayU LazyPay Aligned)

| Persona | Status | Credit Limit | EMI Options | Test Case |
|---------|--------|--------------|-------------|-----------|
| Rajesh Kumar | ❌ Not Eligible | ₹0 | None | New user (<7 days) - fraud blocked |
| Priya Sharma | ❌ Not Eligible | ₹0 | None | Risky user - high return rate (18%) |
| Amit Patel | ✅ Approved | ₹10,000 | 3 (15-day, 3mo, 6mo) | Growing tier - 25 transactions |
| Sneha Reddy | ✅ Approved | ₹30,000 | 4 (15-day, 3mo, 6mo, 9mo) | Regular tier - 48 transactions |
| Vikram Singh | ✅ Approved | ₹100,000 | 5 (15-day, 3mo, 6mo, 9mo, 12mo) | Power tier - 237 transactions |

---

## Project Structure

```
BNPL/
├── backend/
│   ├── synthetic-data-gen/     # Data generation module
│   │   ├── main.py             # Entry point: python main.py
│   │   ├── config.py           # 5 persona configurations
│   │   ├── generators/         # User, transaction, merchant generators
│   │   └── output/
│   │       └── grabon_bnpl.db  # SQLite database (generated)
│   │
│   ├── mcp-server/             # MCP server module
│   │   ├── server.py           # FastMCP server (python server.py)
│   │   ├── tools/              # 5 MCP tools
│   │   │   ├── get_user_profile.py
│   │   │   ├── calculate_credit_score.py
│   │   │   ├── generate_emi_options.py
│   │   │   ├── explain_credit_decision.py
│   │   │   └── get_user_transactions.py
│   │   ├── db/                 # Database manager (singleton)
│   │   ├── utils/              # Scoring engine, EMI calculator
│   │   └── prompts/            # Azure OpenAI narrative prompts
│   │
│   ├── api/                    # FastAPI REST server
│   │   ├── main.py
│   │   ├── routes/
│   │   │   └── checkout.py     # POST /api/checkout/eligibility
│   │   ├── middleware/         # Rate limiting, CORS, error handling
│   │   └── services/           # MCP client, Azure OpenAI client
│   │
│   ├── run.py                  # Backend server entry (python run.py)
│   ├── requirements.txt        # All Python dependencies
│   └── .env                    # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── CheckoutContainer.jsx
│   │   │   ├── PaymentMethods.jsx
│   │   │   ├── BNPLWidget.jsx
│   │   │   ├── EMIOptionCard.jsx
│   │   │   └── FooterBar.jsx
│   │   ├── hooks/              # Custom React hooks
│   │   │   ├── useBNPLState.js
│   │   │   └── useEligibilityCheck.js
│   │   ├── services/           # API client
│   │   │   └── api.js
│   │   └── data/
│   │       └── mockData.js     # 5 user personas (mock mode)
│   │
│   ├── package.json
│   └── .env                    # Frontend environment variables
│
├── .env.example                # Example environment variables
└── README.md                   # This file
```

---

## Environment Variables

**Quick Setup:**

1. Copy `.env.example` to create your environment files:

```bash
# Backend environment
cp .env.example backend/.env

# Frontend environment  
cp .env.example frontend/.env
```

2. Edit `backend/.env` and add your Azure OpenAI credentials (get from Azure Portal)
3. Keep default values for local development

**📄 See `.env.example` for complete list of all environment variables with documentation.**

### Backend (`.env` in `backend/` folder)

```env
# Database
DATABASE_PATH=./synthetic-data-gen/output/grabon_bnpl.db

# Azure OpenAI (for AI narratives)
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
AZURE_OPENAI_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5.1
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# MCP Server
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8001

# FastAPI
API_HOST=localhost
API_PORT=8000
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend (`.env` in `frontend/` folder)

```env
# Backend API URL (must match backend API_PORT)
VITE_API_BASE_URL=http://localhost:8000

# Feature flags (optional)
VITE_DEFAULT_API_MODE=false
VITE_SHOW_PERSONA_SWITCHER=true
```

**Note:** Frontend environment variables must start with `VITE_` prefix to be accessible in Vite.

---

## API Documentation

### Health Check

```bash
GET http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "mcp_server": "connected"
}
```

### Check BNPL Eligibility

```bash
POST http://localhost:8000/api/checkout/eligibility
Content-Type: application/json

{
  "user_id": "USR_SNEHA",
  "product_id": "PROD_001",
  "amount": 12499
}
```

**Response (PayU LazyPay Format):**
```json
{
  "status": "approved",
  "credit_limit": 30000.0,
  "reason": "Great news! You've been approved for ₹30,000 credit because you've made 48 purchases with very few returns (2% return rate), and you shop across multiple categories...",
  "transaction_history": {
    "total_purchases": 48,
    "avg_order_value": 2850,
    "return_rate": 2.0,
    "member_since": "2024-08-15"
  },
  "emi_options": [
    {
      "id": 1,
      "duration": 0.5,
      "monthly_payment": 12499.0,
      "tag": "Pay in 15 days - No interest",
      "total_amount": 12499.0,
      "interest_rate": 0.0,
      "due_date": "2026-04-23",
      "is_one_time_payment": true
    },
    {
      "id": 2,
      "duration": 3,
      "monthly_payment": 4291.67,
      "tag": "Short EMI",
      "total_amount": 12875.0,
      "interest_rate": 12.0
    },
    {
      "id": 3,
      "duration": 6,
      "monthly_payment": 2216.67,
      "tag": "Standard EMI",
      "total_amount": 13300.0,
      "interest_rate": 14.0
    },
    {
      "id": 4,
      "duration": 9,
      "monthly_payment": 1511.11,
      "tag": "Flexible EMI",
      "total_amount": 13600.0,
      "interest_rate": 16.0
    }
  ],
  "emi_provider": "PayU LazyPay"
}
```

---

## Testing

### Test All Personas via API

```bash
# Test each persona
for user in USR_RAJESH USR_PRIYA USR_AMIT USR_SNEHA USR_VIKRAM; do
  echo "Testing $user..."
  curl -s -X POST http://localhost:8000/api/checkout/eligibility \
    -H "Content-Type: application/json" \
    -d "{\"user_id\":\"$user\",\"product_id\":\"PROD_001\",\"amount\":12499}" \
    | python -m json.tool
  echo "---"
done
```

### Expected Results (PayU LazyPay Aligned)

✅ **USR_RAJESH**: `status: "not_eligible"` (new user <7 days)  
✅ **USR_PRIYA**: `status: "not_eligible"` (high return rate 18%)  
✅ **USR_AMIT**: `status: "approved"`, `credit_limit: 10000` (Growing tier)  
✅ **USR_SNEHA**: `status: "approved"`, `credit_limit: 30000` (Regular tier)  
✅ **USR_VIKRAM**: `status: "approved"`, `credit_limit: 100000` (Power tier)

---

## Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

---

### Database not found

**Error**: `Database file not found: grabon_bnpl.db`

**Solution**:
```bash
cd backend/synthetic-data-gen
python main.py  # Regenerate database
```

---

### Frontend shows "Backend not running"

**Check backend is running:**
```bash
curl http://localhost:8000/health
```

If it fails, restart backend:
```bash
cd backend
python run.py
```

Then **restart frontend dev server** (Vite needs restart to pick up backend):
```bash
cd frontend
# Press Ctrl+C to stop
npm run dev
```

---

### MCP server not connecting

**Check MCP server is running:**
```bash
cd backend/mcp-server
python server.py
```

**Check MCP config** in `.claude/mcp.json` has correct paths (use absolute paths, not relative).

---

## Credit Scoring Algorithm

### 6 Factors (Total 100 points)

1. **Purchase Frequency (30 points)**
   - Transactions per month
   - Linear scale: 0-10 txns/month → 0-30 points

2. **Return Behavior (25 points)**
   - Inverse of return rate
   - 0% returns → 100/100 → 25 points
   - >10% returns → Auto-rejection

3. **GMV Trajectory (20 points)**
   - Spending trend over time (linear regression)
   - Upward trend → higher score

4. **Category Diversity (10 points)**
   - Number of unique shopping categories
   - 6 categories (max) → 100/100 → 10 points

5. **Coupon Redemption (10 points)**
   - Percentage of orders using coupons
   - Quality signal: smart shoppers use deals

6. **Fraud Check (5 points)**
   - New users (<7 days) → AUTO-BLOCK
   - Active users → 100/100 → 5 points

### Credit Tiers (PayU LazyPay Aligned)

| Tier | Score Range | Credit Limit | EMI Options |
|------|-------------|--------------|-------------|
| New User | <40 | ₹0 | None |
| Risky | 40-55 | ₹0 | None |
| Growing | 56-70 | ₹10,000 | 15-day, 3/6 months |
| Regular | 71-85 | ₹30,000 | 15-day, 3/6/9 months |
| Power | 86-100 | ₹100,000 | 15-day, 3/6/9/12 months |

**Note**: 15-day option = Pay full amount in 15 days @ 0% interest (PayU LazyPay primary offering)

---

## Key Architecture Decisions

### 1. Why Synchronous SQLite (Not Async)?

**Decision**: Use `sqlite3` (synchronous) with thread-local connections instead of `aiosqlite` (async).

**Rationale**:
- **MCP Specification**: Standard MCP tools are synchronous by design
- **Claude Desktop Integration**: Expects synchronous tool execution
- **SQLite Architecture**: Single-writer database - async provides no concurrency benefit
- **Performance Profile**: Database queries are <10ms (2% of total latency)
  - Total latency: ~450ms
  - LLM calls: ~300ms (67% - the real bottleneck)
  - Credit scoring: ~30ms (7%)
  - Database: ~10ms (2%)
  - EMI calculation: ~5ms (1%)
- **Code Simplicity**: No async/await propagation through entire codebase
- **Demo Scope**: 5 personas, 318 transactions - not production scale
- **Debugging**: Clear stack traces without coroutine complexity

**Production Migration Path**: For 8M+ transactions/month scale, migrate to **PostgreSQL** with connection pooling (asyncpg or psycopg2 pool) and row-level locking (`SELECT ... FOR UPDATE`).

---

### 2. Why Singleton Pattern for Database Manager?

**Decision**: Implement singleton `DatabaseManager` with thread-local connections.

**Rationale**:
- **One instance per process** - prevents multiple connection pools
- **Thread-local storage** - each thread gets its own SQLite connection (avoids threading issues)
- **Automatic connection reuse** - connections cached within thread
- **Safe for multi-threaded MCP server** - no race conditions
- **Double-check locking pattern** - thread-safe singleton initialization

**Code Pattern**:
```python
class DatabaseManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def connection(self):
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn
```

---

### 3. Why MCP Protocol?

**Decision**: Expose credit scoring via Model Context Protocol (MCP) instead of direct API calls.

**Rationale**:
- **Claude Integration**: MCP is Claude's native protocol for tool use
- **Structured Interaction**: Well-defined tool schemas (Pydantic models)
- **Composability**: Tools can be chained (e.g., get_user_profile → calculate_credit_score → explain_credit_decision)
- **Debugging**: Tools can be tested independently in Claude Desktop/Code
- **Future-Proof**: MCP is Anthropic's standard for AI-application integration

**Trade-off**: Adds a layer between frontend and database, but enables Claude-powered reasoning about credit decisions.

---

### 4. Why Azure OpenAI (GPT-5.1) for Narratives?

**Decision**: Use Azure OpenAI for credit narratives instead of Claude API directly.

**Rationale**:
- **Cost**: GPT-5.1 is cheaper than Claude Opus for narrative generation
- **Latency**: Azure OpenAI has lower latency for our region
- **Structured Output**: Good at following templates (see `prompts/credit_narrative.py`)
- **Fallback Architecture**: Code supports both Claude and Azure OpenAI via factory pattern

**Code Pattern**:
```python
def get_ai_client():
    provider = config.AI_PROVIDER.lower()
    if provider == "azure":
        return AzureOpenAIClient()
    else:
        return ClaudeClient()
```

Users can switch by setting `AI_PROVIDER=claude` in `.env`.

---

### 5. Why 6-Factor Scoring Model?

**Decision**: Use 6 behavioral signals instead of traditional credit bureau data.

**Rationale**:
- **E-commerce Context**: Traditional credit scores don't capture shopping behavior
- **No Credit Bureau Required**: Works for users without formal credit history
- **Real-time Decisioning**: All factors computed from transactional data in database
- **Interpretability**: Each factor has clear business logic (no black box)
- **RBI Compliance**: Includes affordability check (50% EMI-to-income rule)

**Why These 6 Factors?**
- **Purchase Frequency (30%)**: Measures engagement and reliability
- **Return Behavior (25%)**: High returns = quality/fraud risk (>10% auto-reject)
- **GMV Trajectory (20%)**: Upward spending trend = income growth signal
- **Category Diversity (10%)**: Shopping across categories = stable user
- **Coupon Redemption (10%)**: Quality signal (smart shoppers use deals)
- **Fraud Check (5%)**: Velocity check for new accounts (<7 days blocked)

---

### 6. Why Synthetic Data Generation?

**Decision**: Generate synthetic transaction data using Evidently AI instead of using real user data.

**Rationale**:
- **Privacy**: No real user PII required for demo
- **Reproducibility**: Same data every time for testing
- **Controlled Scenarios**: Can test edge cases (new users, high returns, etc.)
- **Realistic Distributions**: Evidently AI generates statistically plausible data
- **Fast Iteration**: No need for data export pipelines

**Production Path**: Replace synthetic data generation with database connector to production transaction warehouse.

---

### 7. PayU Mock Fallback Pattern

**Decision**: Implement mock PayU client that activates automatically when real credentials unavailable.

**Why Mock Instead of Real PayU Sandbox?**
- **PayU Merchant Onboarding**: Requires 7-10 days for approval + business documents
- **No Sandbox Without Credentials**: PayU doesn't offer public test credentials
- **Demo Portfolio Project**: Mock demonstrates integration architecture without merchant account
- **Zero External Dependencies**: Runs offline, no API rate limits or downtime

**Implementation Pattern**:

```python
# Factory automatically selects mock vs real
def get_payu_client():
    has_real_credentials = (
        settings.PAYU_ENABLED and
        settings.PAYU_MERCHANT_KEY not in ["gtKFFx", "", None] and  # Not default
        settings.PAYU_MERCHANT_SALT not in ["4R38IvwiV57FwVpsgOvTXBdLE4tHUXFW", "", None]
    )
    
    if has_real_credentials:
        return PayULazyPayClient()  # Real API calls
    else:
        return MockPayUClient()  # No network, instant responses
```

**Mock vs Real Comparison**:

| Feature | MockPayUClient | PayULazyPayClient |
|---------|----------------|-------------------|
| **API Calls** | ❌ None (local only) | ✅ HTTPS to test.payu.in |
| **Credentials Required** | ❌ No | ✅ Yes (merchant key + salt) |
| **Response Format** | ✅ Identical to PayU | ✅ Real PayU format |
| **EMI Plans** | ✅ Realistic (HDFC 3/6, ICICI 9/12) | ✅ Real bank plans |
| **Latency** | <1ms (instant) | ~300-500ms (network) |
| **Tier-Based Filtering** | ✅ Yes (mimics PayU rules) | ✅ Yes (PayU backend) |
| **Cost** | Free | ₹2 + 2% per transaction |
| **Uptime** | 100% (offline) | ~99.9% (PayU SLA) |

**How Mock Client Works**:

1. **Generates PayU-Format Responses**:
```python
# Mock returns same structure as real PayU
mock_emi_details = {
    "HDFC": {
        "3": {"emi_amount": 4166.33, "interest_rate": 0.0},
        "6": {"emi_amount": 2150.00, "interest_rate": 2.0}
    },
    "ICICI": {
        "9": {"emi_amount": 1500.00, "interest_rate": 5.0},
        "12": {"emi_amount": 1133.33, "interest_rate": 8.0}
    }
}
```

2. **Applies Same Business Rules**:
- Growing tier (₹15K): Only 3/6 months
- Regular tier (₹25K): 3/6/9 months
- Power tier (₹50K): All tenures (3/6/9/12)

3. **Logs All Operations**:
```
🎭 [MOCK PayU] Calculating EMI for USR_AMIT, amount ₹12,499
✅ [MOCK PayU] Generated 2 EMI options for USR_AMIT
```

**How to Upgrade to Real PayU**:

1. **Apply for PayU Merchant Account**: https://dashboard.payu.in/merchant-onboarding
2. **Get Credentials** (7-10 business days):
   - Merchant Key (e.g., `jpMwWs`)
   - Merchant Salt (e.g., `U8mfZGf7`)
3. **Update `.env`**:
```env
PAYU_MERCHANT_KEY=jpMwWs  # Your real key
PAYU_MERCHANT_SALT=U8mfZGf7  # Your real salt
PAYU_ENABLED=true
```
4. **Restart Backend** - Factory auto-detects real credentials and switches to `PayULazyPayClient`

**No code changes required** - just add credentials.

**Benefits**:
- ✅ **Demo-Ready**: Works immediately without waiting for PayU approval
- ✅ **Same Interface**: `calculate_emi_offers()` signature identical for both clients
- ✅ **Production Pattern**: Demonstrates proper abstraction layer for payment gateway integration
- ✅ **Easy Testing**: Predictable responses, no network flakiness
- ✅ **Cost-Free Development**: No transaction fees during development

**Trade-off**: Mock doesn't test real PayU API edge cases (rate limits, webhook delays, bank downtimes). For production launch, test with real PayU sandbox before going live.

---

### 8. PayU LazyPay Strategic Partnership

**GrabOn Financial Services Strategy:**

GrabOn is building two new financial services verticals powered by its transaction data advantage and strategic partnerships with **Poonawalla Fincorp** (NBFC with lending license) and **PayU** (India's leading payment infrastructure):

1. **GrabCredit BNPL**: Consumer-facing Buy Now, Pay Later products at checkout
2. **Merchant Credit Lines**: Working capital credit lines for merchants, underwritten using GrabOn's proprietary behavioral transaction data

**PayU LazyPay Integration:**

This system implements **PayU LazyPay's actual BNPL terms**:

| Feature | PayU LazyPay Implementation |
|---------|---------------------------|
| **Primary Offering** | 15-day @ 0% interest (one-time payment) |
| **EMI Options** | 3/6/9/12 months (tier-based) |
| **EMI Interest Rates** | 12% (3mo), 14% (6mo), 16% (9mo), 18% (12mo) p.a. |
| **Credit Limits** | ₹10K (growing), ₹30K (regular), ₹100K (power) |
| **Credit Check** | None (behavioral scoring only) |
| **Documentation** | None required (instant approval) |
| **Approval Speed** | < 1 second (real-time) |
| **Lending Partners** | RBL Bank / DMI Finance (via PayU) |
| **Strategic Partner** | PayU (payment infrastructure) + Poonawalla Fincorp (NBFC) |

**How PayU LazyPay Works:**

1. **Primary Flow**: User selects "Pay in 15 days" @ 0% interest (full amount due in 15 days)
2. **EMI Conversion**: User can convert to EMI (3/6/9/12 months) at checkout or later
3. **Behavioral Scoring**: Credit decision based on GrabOn transaction history (no CIBIL check)
4. **Instant Approval**: Credit limit assigned in real-time (<1 second)
5. **PayU Infrastructure**: Payment processing via PayU's API
6. **NBFC Backing**: Loans underwritten by Poonawalla Fincorp (regulated NBFC)

**Partnership Benefits:**

- ✅ **PayU Expertise**: Leverage India's leading payment infrastructure
- ✅ **NBFC Compliance**: Poonawalla Fincorp ensures RBI regulatory compliance
- ✅ **Data Advantage**: GrabOn's proprietary transaction data powers credit scoring
- ✅ **Instant Decisioning**: No credit bureau checks, fully behavioral
- ✅ **Scalable Infrastructure**: PayU handles payment processing at scale

**Implementation Details:**

This project demonstrates the complete integration architecture:
- Mock PayU client for demo (no credentials required)
- Factory pattern for seamless mock → real client upgrade
- Actual PayU LazyPay terms (15-day @ 0%, EMI at 12-18% p.a.)
- Credit limits matching PayU tiers (₹10K/₹30K/₹100K)
- Production-ready API structure for real PayU integration

---

## What I'd Do Differently With More Time

### 1. Database Migration to PostgreSQL

**Current Limitation**: SQLite is single-writer, unsuitable for production concurrency.

**What I'd Do**:
- Migrate to **PostgreSQL** with asyncpg connection pool
- Implement **row-level locking** (`SELECT ... FOR UPDATE`) for credit limit updates
- Add **read replicas** for user profile queries (separate read/write traffic)
- Use **pgBouncer** for connection pooling (handle 1000s of concurrent requests)

**Impact**: Support 8M+ transactions/month (100 req/sec sustained)

---

### 2. Implement Full Transaction Lifecycle

**Current Limitation**: System only handles eligibility checks, not actual purchases or EMI repayments.

**What I'd Add**:
- **Purchase Confirmation**: Lock credit limit when user confirms EMI plan
- **Credit Utilization Tracking**: Real-time tracking of outstanding dues
- **EMI Repayment Engine**: Monthly deductions, late fees, interest calculations
- **Payment Gateway Integration**: PayU/Razorpay for actual payments
- **Credit Limit Adjustments**: Auto-increase limits after 6 on-time payments

**Impact**: Full BNPL lifecycle from eligibility → purchase → repayment → collections

---

### 3. Add Fraud Detection ML Model

**Current Limitation**: Fraud check is rule-based (new users <7 days blocked).

**What I'd Add**:
- **Anomaly Detection**: Isolation Forest or Autoencoder for unusual patterns
- **Device Fingerprinting**: Detect multi-accounting (same device, different users)
- **Velocity Checks**: Block >3 credit applications in 24 hours
- **Graph Analysis**: Detect fraud rings (connected users with similar patterns)
- **Real-time Scoring**: Sub-50ms fraud score using pre-trained model

**Impact**: Reduce fraud rate from ~2% to <0.5% (industry best-in-class)

---

### 4. Implement Caching Layer (Redis)

**Current Limitation**: Every API call hits database and LLM (slow and expensive).

**What I'd Add**:
- **User Profile Cache**: Cache user data for 1 hour (TTL)
- **Credit Score Cache**: Cache credit decisions for 24 hours
- **LLM Response Cache**: Cache AI narratives by user_id + amount hash
- **Rate Limiting**: Use Redis for sliding window rate limits (60 req/min)
- **Session Management**: Store JWT tokens in Redis (not in-memory)

**Impact**: Reduce latency from ~450ms to <100ms for cached requests, save 70% on LLM costs

---

### 5. Add Comprehensive Testing Suite

**Current Limitation**: No automated tests (manual testing only).

**What I'd Add**:
- **Unit Tests**: pytest for credit scoring engine, EMI calculator
- **Integration Tests**: Test FastAPI endpoints with mocked database
- **MCP Tool Tests**: Test each MCP tool independently
- **Load Tests**: Locust tests for 100 req/sec sustained load
- **Regression Tests**: Snapshot testing for AI narratives (catch prompt drift)

**Impact**: Catch bugs before production, safe refactoring

---

### 6. Build Admin Dashboard

**Current Limitation**: No visibility into system performance or user behavior.

**What I'd Add**:
- **Credit Decision Analytics**: Approval rate by tier, rejection reasons breakdown
- **User Cohort Analysis**: Segment users by credit tier, shopping behavior
- **Model Performance**: Track credit score distribution, EMI default rates
- **LLM Cost Tracking**: Monitor Azure OpenAI API usage and costs
- **Alerting**: Slack/PagerDuty alerts for high rejection rates or API errors

**Impact**: Data-driven optimization of credit policies

---

### 7. Implement A/B Testing Framework

**Current Limitation**: Can't experiment with credit policies or EMI terms.

**What I'd Add**:
- **Feature Flags**: LaunchDarkly for gradual rollout of new policies
- **Experimentation Platform**: A/B test credit limits (₹15K vs ₹20K for growing tier)
- **Multi-Armed Bandits**: Optimize EMI terms (3/6/9 months vs 3/6/12 months)
- **Causal Impact Analysis**: Measure impact of policy changes on GMV, default rates
- **Personalization**: Different credit limits per user based on predicted LTV

**Impact**: Maximize GMV while minimizing default rate (balance growth and risk)

---

### 8. Add Real-Time Notifications

**Current Limitation**: Users don't know when their credit limit increases or EMI is due.

**What I'd Add**:
- **Email Notifications**: Welcome email, credit approved, EMI reminders
- **SMS Alerts**: 3 days before EMI due date
- **Push Notifications**: Mobile app integration for real-time updates
- **In-App Messaging**: Show credit limit changes on GrabOn homepage
- **WhatsApp Business API**: Send EMI receipts after payment

**Impact**: Reduce late payments by 30%, improve user engagement

---

### 9. Implement GDPR/Privacy Controls

**Current Limitation**: No data retention policy or user consent management.

**What I'd Add**:
- **Data Retention Policy**: Auto-delete transaction data after 7 years
- **Right to Erasure**: API endpoint for users to delete their data
- **Consent Management**: Explicit opt-in for credit scoring
- **Data Anonymization**: Hash PII in logs and analytics
- **Audit Logging**: Track who accessed what data when (compliance)

**Impact**: GDPR compliance, build user trust

---

### 10. Optimize LLM Costs

**Current Limitation**: Every credit decision calls Azure OpenAI (expensive at scale).

**What I'd Do**:
- **Template-Based Narratives**: Use LLM only for edge cases (95% use templates)
- **Batch Processing**: Process 100 narratives in single API call (batch endpoint)
- **Fine-Tuned Model**: Fine-tune smaller model (GPT-3.5) on our narratives
- **Prompt Compression**: Reduce prompt tokens by 50% (use abbreviations)
- **Caching**: Cache narratives by decision type + credit tier (reuse similar messages)

**Impact**: Reduce LLM costs from ₹0.50/decision to ₹0.05/decision (10x reduction)

---

### 11. Build Credit Limit Optimization Engine

**Current Limitation**: Credit limits are rule-based (fixed tiers: ₹15K, ₹25K, ₹50K).

**What I'd Add**:
- **ML Model**: Predict optimal credit limit per user (maximize GMV, minimize default)
- **Reinforcement Learning**: Learn credit policies from historical data
- **Risk-Adjusted Pricing**: Higher interest rates for riskier users (personalized EMI rates)
- **Dynamic Limits**: Adjust credit limit based on recent behavior (weekly updates)
- **Credit Line Increase Offers**: Proactively offer limit increases to good users

**Impact**: Increase GMV by 25% (serve more users at optimal limits)

---

### 12. Add Multi-Tenancy Support

**Current Limitation**: Hardcoded for GrabOn (single merchant).

**What I'd Add**:
- **Merchant Onboarding**: API for merchants to integrate BNPL
- **Merchant-Specific Policies**: Different credit tiers per merchant
- **White-Label UI**: Customizable BNPL widget (merchant branding)
- **Revenue Sharing**: Track merchant fees (2% + ₹10/transaction)
- **Merchant Dashboard**: Each merchant sees their BNPL analytics

**Impact**: Turn into SaaS product (sell to 100+ e-commerce merchants)

---

## License

MIT License - GrabOn BNPL Project

---

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review backend logs: `backend/run.py` console output
3. Check browser console (F12) for frontend errors
4. Verify all 3 services are running (MCP server, backend API, frontend dev server)
