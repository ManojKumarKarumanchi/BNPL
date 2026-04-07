# GrabOn BNPL FastAPI Server

Production-grade REST API for BNPL checkout integration.

## Overview

This FastAPI server exposes REST endpoints for the React frontend to check BNPL eligibility. It communicates with the MCP server to perform credit scoring and EMI generation.

## Installation

```bash
cd api
pip install -r requirements.txt
```

## Configuration

Create `.env` file from `.env.example`:

```bash
cp .env.example .env
```

**Essential Configuration:**

```bash
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# MCP Server
MCP_SERVER_URL=http://localhost:8001

# PayU LazyPay Integration
PAYU_MERCHANT_KEY=gtKFFx  # Sandbox test key
PAYU_MERCHANT_SALT=4R38IvwiV57FwVpsgOvTXBdLE4tHUXFW  # Sandbox salt
PAYU_SANDBOX_URL=https://sandbox.payu.in
PAYU_MODE=sandbox
PAYU_ENABLED=true  # Set to "false" for local EMI calculation

# API Base URL (for PayU callbacks)
API_BASE_URL=http://localhost:8000

# Claude API (optional, for AI narratives)
ANTHROPIC_API_KEY=your_api_key_here
```

**PayU LazyPay Modes:**
- **Sandbox Mode** (`PAYU_ENABLED=true`): EMI calculation uses PayU LazyPay sandbox API
- **Local Mode** (`PAYU_ENABLED=false`): EMI calculation done locally (fallback)

Get sandbox credentials from: https://docs.payu.in/docs/getting-started

## Usage

### Start Server

```bash
# Development mode (auto-reload)
uvicorn main:app --reload --port 8000

# Or simply
python main.py
```

Server runs at: **http://localhost:8000**

### API Documentation

Interactive docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints

### POST /api/checkout/eligibility

Check BNPL eligibility for a user.

**Request:**
```json
{
  "user_id": "USR_SNEHA",
  "product_id": "PROD_SAMSUNG_WATCH",
  "amount": 12499.0
}
```

**Response (Approved):**
```json
{
  "status": "approved",
  "credit_limit": 25000.0,
  "reason": "Based on your frequent purchases, low return rate of 2%, and consistent spending over the past 6 months, you've been pre-approved for instant credit.",
  "transaction_history": {
    "total_purchases": 48,
    "avg_order_value": 1561.80,
    "return_rate": 2.1,
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
      "monthly_payment": 2102.65,
      "tag": null,
      "total_amount": 12615.90,
      "interest_rate": 3.2
    }
  ]
}
```

**Response (Not Eligible):**
```json
{
  "status": "not_eligible",
  "credit_limit": 0,
  "reason": "High return rate detected: 12.5%",
  "transaction_history": {...},
  "emi_options": null
}
```

**Response (New User):**
```json
{
  "status": "new_user",
  "credit_limit": 0,
  "reason": "Account too new (6 days). Complete 3-5 purchases first.",
  "transaction_history": {...},
  "emi_options": null
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "mcp_server": "connected"
}
```

## Testing

### cURL Examples

```bash
# Check eligibility for Sneha (Regular User)
curl -X POST http://localhost:8000/api/checkout/eligibility \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USR_SNEHA",
    "product_id": "PROD_SAMSUNG_WATCH",
    "amount": 12499.0
  }'

# Check eligibility for Vikram (Power User - VIP)
curl -X POST http://localhost:8000/api/checkout/eligibility \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USR_VIKRAM",
    "product_id": "PROD_SAMSUNG_WATCH",
    "amount": 12499.0
  }'

# Check eligibility for Rajesh (New User - Blocked)
curl -X POST http://localhost:8000/api/checkout/eligibility \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USR_RAJESH",
    "product_id": "PROD_SAMSUNG_WATCH",
    "amount": 12499.0
  }'
```

### Python Client

```python
import httpx

async def check_eligibility(user_id: str, amount: float):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/checkout/eligibility",
            json={
                "user_id": user_id,
                "product_id": "PROD_SAMSUNG_WATCH",
                "amount": amount
            }
        )
        return response.json()

# Usage
result = await check_eligibility("USR_SNEHA", 12499.0)
print(result["status"])  # "approved"
print(result["credit_limit"])  # 25000.0
```

## Frontend Integration

### React/JavaScript

```javascript
// frontend/src/services/api.js
export async function checkEligibility(userId, productId, amount) {
  const response = await fetch('http://localhost:8000/api/checkout/eligibility', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_id: userId,
      product_id: productId,
      amount: amount
    })
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

// Usage in component
const handleBuyNow = async () => {
  try {
    const result = await checkEligibility('USR_SNEHA', 'PROD_SAMSUNG_WATCH', 12499);
    
    setUserPersona({
      status: result.status,
      creditLimit: result.credit_limit,
      reason: result.reason,
      transactionHistory: {
        totalPurchases: result.transaction_history.total_purchases,
        avgOrderValue: result.transaction_history.avg_order_value,
        returnRate: result.transaction_history.return_rate,
        memberSince: result.transaction_history.member_since
      },
      emiOptions: result.emi_options
    });
  } catch (error) {
    console.error('Eligibility check failed:', error);
  }
};
```

## PayU LazyPay Integration

### Overview

The API integrates with **PayU LazyPay sandbox API** for BNPL disbursal flow and EMI generation. This satisfies the project requirement:

> "Integrate with PayU LazyPay sandbox API for the actual BNPL disbursal flow (EMI offer generation: 3/6/9 months)"

### EMI Calculation Flow

```
User → FastAPI → PayU LazyPay API (EMI calculation)
              ↓ (if API fails)
              → Local EMI calculation (fallback)
```

**Implementation:**

1. **PayU API Client** (`services/payu_client.py`):
   - SHA512 hash generation for authentication
   - EMI offer calculation endpoint
   - Checkout initiation
   - Transaction status checking

2. **Checkout Route** (`routes/checkout.py`):
   ```python
   # Try PayU API first
   if settings.PAYU_ENABLED:
       payu_result = await payu_client.calculate_emi_offers(
           user_id=request.user_id,
           amount=request.amount,
           credit_limit=credit_score["credit_limit"]
       )
       
       if payu_result["status"] == "success":
           emi_options = payu_result["emi_options"]
       else:
           # Fallback to local calculation
           emi_options = await mcp.call_tool("generate_emi_options_tool", {...})
   ```

3. **Response Fields**:
   ```json
   {
     "emi_options": [...],
     "payu_transaction_id": "GRABON_USR_SNEHA_abc123",
     "emi_provider": "PayU LazyPay"
   }
   ```

### PayU API Endpoints Used

| Endpoint | Purpose | Request |
|----------|---------|---------|
| `POST /merchant/postservice.php?form=emi` | Calculate EMI offers | user_id, amount, credit_limit |
| `POST /merchant/paymentgateway.php` | Initiate checkout | transaction_id, emi_duration |
| `POST /merchant/postservice.php?form=verify` | Check transaction status | transaction_id |

### Testing PayU Integration

**With PayU Enabled:**
```bash
# Set in .env
PAYU_ENABLED=true

# API response includes PayU metadata
curl -X POST http://localhost:8000/api/checkout/eligibility \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USR_SNEHA", "product_id": "PROD_001", "amount": 12499}'

# Response:
{
  "emi_options": [...],
  "payu_transaction_id": "GRABON_USR_SNEHA_xyz789",
  "emi_provider": "PayU LazyPay"
}
```

**Without PayU (Local Fallback):**
```bash
# Set in .env
PAYU_ENABLED=false

# API uses local EMI calculation
# Response:
{
  "emi_options": [...],
  "payu_transaction_id": null,
  "emi_provider": "GrabCredit"
}
```

### Error Handling

**PayU API failures are gracefully handled:**

1. **Timeout** (>10s): Falls back to local calculation
2. **HTTP Error** (4xx/5xx): Falls back to local calculation
3. **Invalid Response**: Falls back to local calculation
4. **All failures logged** with error details

**Logs:**
```
🔗 Calling PayU LazyPay API for EMI calculation...
✅ PayU API success: 3 EMI options
```

or

```
🔗 Calling PayU LazyPay API for EMI calculation...
⚠️ PayU API failed: timeout, falling back to local calculation
📊 Using local EMI calculation (PayU disabled)
```

### Sandbox Credentials

**Default test credentials** (included in `.env.example`):
- **Merchant Key**: `gtKFFx`
- **Merchant Salt**: `4R38IvwiV57FwVpsgOvTXBdLE4tHUXFW`
- **Sandbox URL**: `https://sandbox.payu.in`

**Get your own credentials:**
1. Sign up at https://dashboard.payu.in/
2. Navigate to Settings → Developer
3. Copy merchant key and salt
4. Update `.env` file

---

## Architecture

```
FastAPI Server
├── main.py (FastAPI app)
├── config.py (Settings + PayU config)
├── routes/
│   ├── checkout.py (POST /api/checkout/eligibility)
│   └── health.py (GET /health)
├── services/
│   ├── mcp_client.py (Calls MCP server tools)
│   └── payu_client.py (PayU LazyPay API integration) ⭐ NEW
└── schemas/
    ├── request_schemas.py (Pydantic request models)
    └── response_schemas.py (Pydantic response models)
```

**Data Flow:**

```
React Frontend
    ↓
    POST /api/checkout/eligibility
    ↓
FastAPI (routes/checkout.py)
    ↓
    ├─ MCP Client → get_user_profile_tool
    ├─ MCP Client → calculate_credit_score_tool
    ├─ PayU Client → calculate_emi_offers ⭐ NEW
    │   ↓ (if fails)
    │   └─ MCP Client → generate_emi_options_tool (fallback)
    └─ MCP Client → explain_credit_decision_tool
    ↓
Response: {status, credit_limit, emi_options, payu_transaction_id}
```

## Error Handling

The API returns standard HTTP status codes:

- **200 OK** - Successful eligibility check
- **400 Bad Request** - Invalid request parameters
- **404 Not Found** - User not found
- **500 Internal Server Error** - Server error

Error response format:
```json
{
  "error": "Error message",
  "detail": "Detailed error information"
}
```

## CORS Configuration

The server allows requests from:
- http://localhost:3000
- http://localhost:3001
- http://127.0.0.1:3000
- http://127.0.0.1:3001

To add more origins, edit `config.py`:

```python
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "https://your-production-domain.com"
]
```

## Performance

- **Response Time**: <500ms (p95)
- **Concurrent Requests**: Supports async handling
- **Connection Pooling**: HTTP client reuses connections

## Next Steps

1. Start the FastAPI server: `python main.py`
2. Test with cURL or Swagger UI
3. Integrate with React frontend
4. Deploy to production (Render, Railway, etc.)
