# GrabOn BNPL Backend - Quick Start Guide

Complete backend stack with **3 modules** ready to demo!

## ✅ What's Built

1. **Synthetic Data Generator** - 318 realistic transactions for 5 personas
2. **MCP Server** - Credit scoring with 6-factor algorithm
3. **FastAPI Server** - REST endpoints for frontend

## 🚀 Quick Start (3 Steps)

### Step 1: Generate Data (One-Time)

```bash
cd backend/synthetic-data-gen
pip install faker pandas numpy sqlalchemy python-dotenv
python main.py
```

**Output:** Database created at `output/grabon_bnpl.db`

✅ **Verify:** You should see 318 transactions generated for 5 personas.

### Step 2: Test MCP Tools

```bash
cd backend/mcp-server
pip install anthropic httpx fastmcp pandas numpy sqlalchemy python-dotenv
python test_tools.py
```

✅ **Verify:** All 5 personas should be scored correctly (Rajesh=new_user, Vikram=power).

### Step 3: Start FastAPI Server

```bash
cd backend/api
pip install fastapi uvicorn httpx pydantic pydantic-settings python-dotenv
python main.py
```

✅ **Server:** http://localhost:8000  
✅ **Docs:** http://localhost:8000/docs

## 📊 Test the Complete Flow

### Option 1: Use Swagger UI

1. Open http://localhost:8000/docs
2. Click "POST /api/checkout/eligibility"
3. Click "Try it out"
4. Enter:
   ```json
   {
     "user_id": "USR_VIKRAM",
     "product_id": "PROD_SAMSUNG_WATCH",
     "amount": 12499
   }
   ```
5. Click "Execute"

**Expected Response:**
```json
{
  "status": "approved",
  "credit_limit": 50000,
  "reason": "...",
  "emi_options": [4 plans including 12-month VIP]
}
```

### Option 2: Use cURL

```bash
curl -X POST http://localhost:8000/api/checkout/eligibility \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USR_VIKRAM",
    "product_id": "PROD_SAMSUNG_WATCH",
    "amount": 12499
  }'
```

### Option 3: Use Python Test Script

```bash
cd backend/api
python test_api.py
```

This tests all 5 personas automatically.

## 🎯 5 Test Personas

| User ID | Name | Status | Credit Limit | EMI Options |
|---------|------|--------|--------------|-------------|
| USR_RAJESH | Rajesh Kumar | new_user | ₹0 | None (blocked <7 days) |
| USR_PRIYA | Priya Sharma | not_eligible | ₹0 | None (18% returns) |
| USR_AMIT | Amit Patel | approved | ₹15,000 | 2 (3, 6 months) |
| USR_SNEHA | Sneha Reddy | approved | ₹15-25K | 2-3 (3, 6, 9 months) |
| USR_VIKRAM | Vikram Singh | approved | ₹50,000 | 4 (3, 6, 9, 12 months) |

## 🔗 Frontend Integration

Update your React frontend to call the API:

```javascript
// frontend/src/services/api.js
export async function checkEligibility(userId, productId, amount) {
  const response = await fetch('http://localhost:8000/api/checkout/eligibility', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, product_id: productId, amount })
  });
  return await response.json();
}

// Usage
const result = await checkEligibility('USR_VIKRAM', 'PROD_SAMSUNG_WATCH', 12499);
console.log(result.status); // "approved"
console.log(result.emi_options); // 4 EMI plans
```

## 📂 Files Overview

```
backend/
├── synthetic-data-gen/
│   ├── main.py                    # Generate data
│   └── output/grabon_bnpl.db      # SQLite database
├── mcp-server/
│   ├── server.py                  # MCP server (optional)
│   ├── tools/                     # 4 credit scoring tools
│   └── test_tools.py              # Test MCP tools
└── api/
    ├── main.py                    # FastAPI server ⭐ START HERE
    ├── routes/checkout.py         # POST /api/checkout/eligibility
    └── test_api.py                # Test all endpoints
```

## 🛠️ Troubleshooting

### Issue: ModuleNotFoundError

**Solution:** Install dependencies in correct folder
```bash
cd backend/api
pip install -r requirements.txt
```

### Issue: Database not found

**Solution:** Generate data first
```bash
cd backend/synthetic-data-gen
python main.py
```

### Issue: Port 8000 already in use

**Solution:** Change port in `.env`
```bash
PORT=8001
```

Or kill the process:
```bash
# Windows
taskkill /F /IM python.exe

# Mac/Linux
pkill -f "python main.py"
```

## ✅ Success Checklist

- [  ] Data generated (318 transactions)
- [ ] MCP tools tested (5 personas scored)
- [ ] FastAPI server running (http://localhost:8000)
- [ ] Swagger docs accessible (http://localhost:8000/docs)
- [ ] API test passed (python test_api.py)
- [ ] Frontend can call API

## 🎬 Demo for Poonawalla Executives

**10-Minute Walkthrough:**

1. **Show Data** (2 min) - Open `generation_report.json`, show 5 personas
2. **Show Scoring** (3 min) - Run `test_tools.py`, explain 6-factor model
3. **Show API** (2 min) - Open Swagger UI, test Vikram (power user)
4. **Show Frontend** (3 min) - React app with real API integration

**Key Talking Points:**
- ✅ Real GrabOn data patterns (96M txn context)
- ✅ Explainable AI (6-factor scoring, not black-box)
- ✅ VIP tiering (₹15K → ₹50K progression)
- ✅ Production-ready (FastAPI, async, error handling)

---

**Need help?** See detailed READMEs in each module:
- [synthetic-data-gen/README.md](synthetic-data-gen/README.md)
- [mcp-server/README.md](mcp-server/README.md)
- [api/README.md](api/README.md)
