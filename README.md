# GrabCredit BNPL - Buy Now, Pay Later System

An AI-powered credit scoring and BNPL eligibility engine for GrabOn's e-commerce platform, powered by Claude AI and Azure OpenAI.

## Overview

GrabCredit analyzes user transaction history to provide instant credit decisions at checkout. Built with:

- **Backend**: FastAPI + MCP Server + Azure OpenAI (GPT-5.1)
- **Frontend**: React + TailwindCSS + Framer Motion
- **Database**: SQLite (synthetic transaction data)
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

✅ **5 User Personas**
- Rajesh Kumar (New User) - 0 transactions, blocked <7 days
- Priya Sharma (Risky) - 8 transactions, approved ₹15K
- Amit Patel (Growing) - 25 transactions, approved ₹15K
- Sneha Reddy (Regular) - 48 transactions, approved ₹15K
- Vikram Singh (Power) - 237 transactions, approved ₹50K

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

### Testing Personas

| Persona | Status | Credit Limit | EMI Options | Test Case |
|---------|--------|--------------|-------------|-----------|
| Rajesh Kumar | ❌ Not Eligible | ₹0 | None | New user (<7 days) - fraud blocked |
| Priya Sharma | ✅ Approved | ₹15,000 | 2 | Risky user with few transactions |
| Amit Patel | ✅ Approved | ₹15,000 | 2 | Growing user - good behavior |
| Sneha Reddy | ✅ Approved | ₹15,000 | 2 | Regular user - consistent shopping |
| Vikram Singh | ✅ Approved | ₹50,000 | 2 | Power user - 237 transactions |

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

**Response:**
```json
{
  "status": "approved",
  "credit_limit": 15000.0,
  "reason": "Great news! You've been approved for ₹15,000 credit because you've made 48 purchases with very few returns (2% return rate), and you shop across multiple categories...",
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
  ]
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

### Expected Results

✅ **USR_RAJESH**: `status: "not_eligible"` (new user <7 days)  
✅ **USR_PRIYA**: `status: "approved"`, `credit_limit: 15000`  
✅ **USR_AMIT**: `status: "approved"`, `credit_limit: 15000`  
✅ **USR_SNEHA**: `status: "approved"`, `credit_limit: 15000`  
✅ **USR_VIKRAM**: `status: "approved"`, `credit_limit: 50000`

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

### Credit Tiers

| Tier | Score Range | Credit Limit | EMI Options |
|------|-------------|--------------|-------------|
| New User | <40 | ₹0 | None |
| Risky | 40-55 | ₹0 | None |
| Growing | 56-70 | ₹15,000 | 3/6 months |
| Regular | 71-85 | ₹25,000 | 3/6/9 months |
| Power | 86-100 | ₹50,000 | 3/6/9/12 months |

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
