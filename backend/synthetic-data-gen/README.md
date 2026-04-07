# GrabOn BNPL Synthetic Data Generator

Generate realistic transaction data for 5 user personas matching frontend expectations.

## Overview

This module uses Evidently AI and Faker to create authentic GrabOn transaction patterns for:

- **Rajesh Kumar** (USR_RAJESH) - New user, 0 transactions
- **Priya Sharma** (USR_PRIYA) - Risky user, 8 transactions, 18% returns
- **Amit Patel** (USR_AMIT) - Growing user, 25 transactions
- **Sneha Reddy** (USR_SNEHA) - Regular user, 48 transactions
- **Vikram Singh** (USR_VIKRAM) - Power user, 237 transactions

## Installation

```bash
cd synthetic-data-gen
pip install -r requirements.txt
```

## Usage

### Generate All Data

```bash
python main.py
```

This will:
1. Create `output/grabon_bnpl.db` SQLite database
2. Generate 6 merchants (Amazon, Flipkart, Myntra, etc.)
3. Create 5 user personas
4. Generate realistic transactions (318 total)
5. Create validation report in `output/generation_report.json`

### Output

```
output/
├── grabon_bnpl.db           # SQLite database
└── generation_report.json   # Validation report
```

## Database Schema

### Tables

- **users**: 5 personas
- **merchants**: 6 real GrabOn merchants
- **transactions**: 318 transactions across all personas

### Key Features

✅ Temporal patterns (transactions distributed over 6-18 months)  
✅ Realistic GMV distribution (log-normal)  
✅ Merchant preferences (Amazon 35%, Flipkart 30%)  
✅ Category preferences (Fashion 24%, Electronics 10%)  
✅ Coupon redemption rates (45% risky → 98% power user)  
✅ Return behavior (0% perfect → 18% risky)  
✅ Fraud signals (new user <7 days)

## Validation

After generation, verify:

```bash
sqlite3 output/grabon_bnpl.db

# Check counts
SELECT user_id, COUNT(*) FROM transactions GROUP BY user_id;

# Check Vikram's stats (should be 237 txns, 0% returns)
SELECT
    COUNT(*) as txn_count,
    AVG(final_amount) as avg_order,
    SUM(CASE WHEN is_returned = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as return_pct
FROM transactions
WHERE user_id = 'USR_VIKRAM';
```

Expected output:
- Txn count: 237
- Avg order: ~₹4,200
- Return %: 0.0%

## Configuration

Edit `config.py` to modify:
- Persona characteristics (avg order value, return rates)
- Merchant data (deal counts, discounts)
- Category distributions
- Coupon codes

## Next Steps

After data generation:
1. Verify `output/grabon_bnpl.db` exists
2. Check `generation_report.json` for validation
3. Proceed to MCP server setup: `cd ../mcp-server`
