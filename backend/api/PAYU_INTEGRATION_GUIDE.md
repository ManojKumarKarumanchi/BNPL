# PayU LazyPay Integration Guide

This guide explains how to set up PayU LazyPay sandbox for EMI/BNPL integration in the GrabCredit system.

## Overview

PayU LazyPay provides Buy Now Pay Later (BNPL) and EMI services. This integration allows:

- Real-time EMI offer calculation
- Multiple tenure options (3/6/9/12 months)
- No-cost EMI and interest-based EMI
- Secure payment processing via PayU

**Current Status:** PayU integration is **DISABLED by default** and uses local EMI calculation fallback.

---

## Why PayU is Disabled by Default

PayU's sandbox environment requires **actual merchant credentials** obtained through their onboarding process. The publicly available test credentials (`gtKFFx`) are examples only and **do not work** with the live sandbox API.

**Error you'll see without valid credentials:**
```
❌ PayU API unexpected error: Expecting value: line 1 column 1 (char 0)
⚠️ PayU API failed: PayU integration error, falling back to local calculation
```

This happens because PayU returns an HTML error page instead of JSON when credentials are invalid.

---

## How to Get PayU Sandbox Credentials

### Step 1: Register as PayU Merchant

1. Visit **PayU Merchant Dashboard**: https://dashboard.payu.in/merchant-onboarding
2. Sign up for a merchant account
3. Complete KYC verification (may require business documents)
4. Request sandbox/test environment access

### Step 2: Get Test Credentials

Once approved, you'll receive:
- **Merchant Key** (e.g., `JP***x`)
- **Merchant Salt** (e.g., `e8c8***`)

These are different from the example credentials in the code.

### Step 3: Access API Documentation

- **Official Docs**: https://docs.payu.in
- **API Reference**: https://docs.payu.in/reference/introduction-api-reference
- **EMI Integration**: https://docs.payu.in/docs/emi-api-integration

---

## Configuration

### 1. Update Environment Variables

Edit `backend/.env`:

```env
# PayU LazyPay Integration
PAYU_ENABLED=true  # Enable PayU API calls
PAYU_MERCHANT_KEY=your-actual-merchant-key-here
PAYU_MERCHANT_SALT=your-actual-merchant-salt-here
```

### 2. Verify Configuration

Check `backend/api/config.py`:

```python
PAYU_ENABLED: bool = os.getenv("PAYU_ENABLED", "false").lower() == "true"
PAYU_MERCHANT_KEY: str = os.getenv("PAYU_MERCHANT_KEY", "gtKFFx")
PAYU_MERCHANT_SALT: str = os.getenv("PAYU_MERCHANT_SALT", "4R38IvwiV57FwVpsgOvTXBdLE4tHUXFW")
PAYU_SANDBOX_URL: str = "https://test.payu.in"
```

---

## API Endpoints Used

### 1. EMI Calculation API

**Endpoint:** `POST https://test.payu.in/merchant/postservice?form=2`

**Request Format:** `application/x-www-form-urlencoded`

**Parameters:**
```python
{
    "key": "your-merchant-key",
    "txnid": "GRABON_USR_AMIT_abc123",
    "amount": "12499",
    "productinfo": "GrabOn BNPL Purchase",
    "firstname": "AMIT",
    "email": "usr_amit@grabon.in",
    "phone": "9999999999",
    "surl": "http://localhost:8000/api/payu/success",
    "furl": "http://localhost:8000/api/payu/failure",
    "hash": "sha512-hash-value",
    "service_provider": "payu_paisa"
}
```

**Hash Calculation:**
```python
hash_string = f"{key}|{txnid}|{amount}|{productinfo}|{firstname}|{email}|||||||||||{salt}"
hash_value = hashlib.sha512(hash_string.encode('utf-8')).hexdigest()
```

**Response Format:**
```json
{
    "status": 1,
    "msg": "SUCCESS",
    "emi_details": {
        "HDFC": {
            "3": {"emi_amount": 4200, "interest_rate": 0},
            "6": {"emi_amount": 2150, "interest_rate": 2.5}
        },
        "ICIC": {
            "3": {"emi_amount": 4200, "interest_rate": 0}
        }
    }
}
```

### 2. Checkout Initiation API

**Endpoint:** `POST https://test.payu.in/merchant/paymentgateway.php`

Used for actual payment processing (not implemented in current demo).

### 3. Transaction Verification API

**Endpoint:** `POST https://test.payu.in/merchant/postservice?form=verify`

Used to check payment status.

---

## Testing PayU Integration

### 1. Enable PayU in Config

```bash
# Edit backend/.env
PAYU_ENABLED=true
```

### 2. Restart Backend

```bash
cd backend
python run.py
```

### 3. Test API Call

```bash
curl -X POST http://localhost:8000/api/checkout/eligibility \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USR_AMIT",
    "product_id": "PROD_001",
    "amount": 12499
  }' | python -m json.tool
```

### 4. Check Logs

**Success:**
```
🔗 Calling PayU EMI API for user USR_AMIT, amount ₹12499
✅ PayU API success: 4 EMI options for USR_AMIT
```

**Failure (Invalid Credentials):**
```
🔗 Calling PayU EMI API for user USR_AMIT, amount ₹12499
⚠️ PayU API returned non-JSON response: text/html
❌ PayU API error: PayU API returned no options, using fallback
⚠️ PayU API failed, falling back to local calculation
```

---

## Local EMI Calculation Fallback

If PayU is disabled or fails, the system automatically falls back to local EMI calculation using the MCP tool `generate_emi_options`.

**Fallback Logic (in `checkout.py`):**

```python
if settings.PAYU_ENABLED:
    payu_result = await payu_client.calculate_emi_offers(...)

    if payu_result["status"] == "success" and payu_result["emi_options"]:
        emi_options = payu_result["emi_options"]
    else:
        logger.warning("PayU API failed, falling back to local calculation")
        emi_options = await generate_emi_options_tool(...)
else:
    # PayU disabled, use local calculation
    emi_options = await generate_emi_options_tool(...)
```

**Benefits of Fallback:**
- ✅ System works without PayU credentials
- ✅ Graceful degradation
- ✅ Same EMI calculation logic
- ✅ No user-facing errors

---

## Test Cards for PayU Sandbox

Once you have valid credentials, use these test cards:

### Credit Cards

| Card Type | Card Number | CVV | Expiry | Result |
|-----------|-------------|-----|--------|--------|
| VISA | 5123 4567 8901 2346 | 123 | Any future | Success |
| MasterCard | 5555 5555 5555 4444 | 123 | Any future | Success |
| AMEX | 3782 8224 6310 005 | 1234 | Any future | Success |

### EMI Test Cards

| Bank | Card Number | Tenure | Result |
|------|-------------|--------|--------|
| HDFC | 4012 0010 3848 8884 | 3/6/9/12 | No Cost EMI |
| ICICI | 5123 4567 8901 2346 | 3/6 | No Cost EMI |
| Axis | 4111 1111 1111 1111 | 3/6/9 | 2.5% Interest |

**Source:** https://docs.payu.in/docs/test-cards-upi-id-and-wallets

---

## Current Implementation Status

### ✅ Implemented

- EMI offer calculation API integration
- Hash generation and authentication
- Response parsing for multiple banks
- Automatic fallback to local calculation
- Error handling and logging
- Environment-based enable/disable

### ❌ Not Implemented

- Actual payment processing (checkout flow)
- Payment status webhooks
- Transaction verification
- Refund/cancellation handling
- LazyPay-specific endpoints (requires separate agreement)

---

## Production Deployment

### 1. Switch to Production Endpoint

Edit `backend/api/config.py`:

```python
PAYU_SANDBOX_URL: str = "https://secure.payu.in"  # Production
PAYU_MODE: str = "production"
```

### 2. Use Production Credentials

```env
PAYU_MERCHANT_KEY=your-production-key
PAYU_MERCHANT_SALT=your-production-salt
PAYU_ENABLED=true
```

### 3. Configure Webhooks

Set up success/failure URLs:

```env
API_BASE_URL=https://yourdomain.com
```

PayU will send callbacks to:
- Success: `https://yourdomain.com/api/payu/success`
- Failure: `https://yourdomain.com/api/payu/failure`

### 4. Implement Webhook Handlers

Create endpoints in `backend/api/routes/payu_webhooks.py`:

```python
@router.post("/payu/success")
async def payu_success_callback(request: Request):
    # Verify hash
    # Update transaction status
    # Notify user
    pass

@router.post("/payu/failure")
async def payu_failure_callback(request: Request):
    # Log failure
    # Notify user
    pass
```

---

## Troubleshooting

### Error: "Expecting value: line 1 column 1 (char 0)"

**Cause:** PayU returned HTML instead of JSON (invalid credentials)

**Solution:**
1. Verify merchant key and salt are correct
2. Check if sandbox access is enabled for your account
3. Set `PAYU_ENABLED=false` to use local calculation

### Error: "PayU API timeout"

**Cause:** PayU sandbox is down or slow

**Solution:**
1. Check PayU status: https://status.payu.in
2. Increase timeout in `payu_client.py`:
   ```python
   self.client = httpx.AsyncClient(timeout=30.0)
   ```
3. Use local fallback

### Error: "Invalid hash"

**Cause:** Hash calculation mismatch

**Solution:**
1. Verify hash formula matches PayU docs
2. Ensure all parameters are in correct order
3. Check salt is correct (common mistake)

---

## Support

**PayU Support:**
- Email: support@payu.in
- Phone: 1800-103-5000
- Documentation: https://docs.payu.in

**LazyPay Specific:**
- Developer Resources: https://linktr.ee/lazypay
- Contact: Requires merchant agreement with PayU

---

## References

- [PayU India Developer Documentation](https://docs.payu.in)
- [PayU EMI Integration Guide](https://docs.payu.in/docs/emi-api-integration)
- [PayU API Reference](https://docs.payu.in/reference/introduction-api-reference)
- [PayU Test Cards](https://docs.payu.in/docs/test-cards-upi-id-and-wallets)
- [PayU BNPL Link and Pay](https://docs.payu.in/docs/collect-payments-with-bnpl-using-link-and-pay)
