-- Database Migration: Add Income, Credit Utilization, and EMI Commitments
-- Date: 2026-04-08
-- Purpose: Enable affordability checks (50% EMI-to-income rule) and real-time credit tracking
-- Reference: COMPREHENSIVE_AUDIT_AND_FIXES.md Sections 2-3

-- ============================================================================
-- STEP 1: Add monthly_income column to users table
-- ============================================================================

-- Check if column exists (SQLite doesn't have IF NOT EXISTS for ALTER TABLE)
-- Run this manually if needed: SELECT * FROM pragma_table_info('users');

ALTER TABLE users ADD COLUMN monthly_income REAL DEFAULT 30000.0;

-- Update income for existing personas (based on their credit tier)
-- Reference: COMPREHENSIVE_AUDIT_AND_FIXES.md Section 2, Step 3

UPDATE users SET monthly_income = 25000  WHERE user_id = 'USR_RAJESH';  -- Entry-level job
UPDATE users SET monthly_income = 35000  WHERE user_id = 'USR_PRIYA';   -- Mid-level
UPDATE users SET monthly_income = 50000  WHERE user_id = 'USR_AMIT';    -- Senior professional
UPDATE users SET monthly_income = 75000  WHERE user_id = 'USR_SNEHA';   -- Well-established
UPDATE users SET monthly_income = 150000 WHERE user_id = 'USR_VIKRAM';  -- High-income (VIP)

-- ============================================================================
-- STEP 2: Create credit_utilization table
-- ============================================================================

CREATE TABLE IF NOT EXISTS credit_utilization (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    purchase_id TEXT UNIQUE NOT NULL,
    purchase_amount REAL NOT NULL,
    outstanding_amount REAL NOT NULL,
    status TEXT DEFAULT 'active',  -- active, paid, cancelled, defaulted
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_util_user ON credit_utilization(user_id);
CREATE INDEX IF NOT EXISTS idx_util_status ON credit_utilization(status);
CREATE INDEX IF NOT EXISTS idx_util_user_active ON credit_utilization(user_id, status) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_util_purchase ON credit_utilization(purchase_id);

-- ============================================================================
-- STEP 3: Create emi_commitments table
-- ============================================================================

CREATE TABLE IF NOT EXISTS emi_commitments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    purchase_id TEXT NOT NULL,
    monthly_emi REAL NOT NULL,
    remaining_months INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (purchase_id) REFERENCES credit_utilization(purchase_id)
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_emi_user ON emi_commitments(user_id);
CREATE INDEX IF NOT EXISTS idx_emi_active ON emi_commitments(user_id, end_date) WHERE end_date >= DATE('now');
CREATE INDEX IF NOT EXISTS idx_emi_purchase ON emi_commitments(purchase_id);

-- ============================================================================
-- STEP 4: Insert sample EMI commitments for testing
-- ============================================================================

-- Example: USR_SNEHA has an active EMI commitment
-- Purchase of ₹18,000 at 6 months = ₹3,100/month EMI
-- This will test affordability calculations

INSERT INTO credit_utilization (user_id, purchase_id, purchase_amount, outstanding_amount, status, created_at)
VALUES ('USR_SNEHA', 'PUR_SAMPLE_001', 18000, 18000, 'active', datetime('now', '-60 days'));

INSERT INTO emi_commitments (user_id, purchase_id, monthly_emi, remaining_months, start_date, end_date)
VALUES (
    'USR_SNEHA',
    'PUR_SAMPLE_001',
    3100,
    4,  -- 4 months remaining (started 2 months ago)
    date('now', '-60 days'),
    date('now', '+120 days')
);

-- Example: USR_VIKRAM has higher EMI commitment but also higher income
-- Purchase of ₹35,000 at 9 months = ₹4,100/month EMI

INSERT INTO credit_utilization (user_id, purchase_id, purchase_amount, outstanding_amount, status, created_at)
VALUES ('USR_VIKRAM', 'PUR_SAMPLE_002', 35000, 35000, 'active', datetime('now', '-90 days'));

INSERT INTO emi_commitments (user_id, purchase_id, monthly_emi, remaining_months, start_date, end_date)
VALUES (
    'USR_VIKRAM',
    'PUR_SAMPLE_002',
    4100,
    6,  -- 6 months remaining (started 3 months ago)
    date('now', '-90 days'),
    date('now', '+180 days')
);

-- ============================================================================
-- STEP 5: Verification Queries
-- ============================================================================

-- Check income values
-- Expected: Rajesh=25K, Priya=35K, Amit=50K, Sneha=75K, Vikram=150K
SELECT user_id, monthly_income FROM users ORDER BY monthly_income;

-- Check credit utilization
-- Expected: 2 active purchases (Sneha, Vikram)
SELECT user_id, purchase_id, outstanding_amount, status FROM credit_utilization;

-- Check EMI commitments
-- Expected: Sneha=₹3,100/month, Vikram=₹4,100/month
SELECT user_id, monthly_emi, remaining_months, end_date FROM emi_commitments WHERE end_date >= DATE('now');

-- Calculate current EMI burden for users
-- This query matches AffordabilityCalculator.calculate_current_emi_burden()
SELECT
    user_id,
    COALESCE(SUM(monthly_emi), 0) as total_monthly_emi
FROM emi_commitments
WHERE end_date >= DATE('now')
GROUP BY user_id;

-- Expected output:
-- USR_SNEHA: ₹3,100
-- USR_VIKRAM: ₹4,100

-- Calculate affordability for sample scenarios
-- USR_SNEHA: Income ₹75K, Current EMI ₹3,100 (4.1%), Max allowed ₹37,500 (50%)
-- Available EMI capacity: ₹34,400
-- Can afford new EMI up to ₹34,400/month

-- USR_VIKRAM: Income ₹150K, Current EMI ₹4,100 (2.7%), Max allowed ₹75,000 (50%)
-- Available EMI capacity: ₹70,900
-- Can afford new EMI up to ₹70,900/month

SELECT
    u.user_id,
    u.monthly_income,
    COALESCE(e.total_emi, 0) as current_emi,
    ROUND(COALESCE(e.total_emi, 0) / u.monthly_income * 100, 2) as emi_percent_of_income,
    ROUND(u.monthly_income * 0.50, 2) as max_allowed_emi,
    ROUND(u.monthly_income * 0.50 - COALESCE(e.total_emi, 0), 2) as available_emi_capacity
FROM users u
LEFT JOIN (
    SELECT user_id, SUM(monthly_emi) as total_emi
    FROM emi_commitments
    WHERE end_date >= DATE('now')
    GROUP BY user_id
) e ON u.user_id = e.user_id
ORDER BY u.monthly_income DESC;

-- ============================================================================
-- ROLLBACK (if needed)
-- ============================================================================

-- To rollback this migration (use with caution):
/*
DROP TABLE IF EXISTS emi_commitments;
DROP TABLE IF EXISTS credit_utilization;
ALTER TABLE users DROP COLUMN monthly_income;  -- Not supported in SQLite
-- For SQLite, you would need to recreate the table without the column
*/

-- ============================================================================
-- NOTES
-- ============================================================================

-- 1. SQLite Limitations:
--    - No ALTER TABLE DROP COLUMN (must recreate table)
--    - No IF NOT EXISTS for ALTER TABLE ADD COLUMN (must check manually)
--    - FOR UPDATE not supported (use BEGIN IMMEDIATE for write locks)

-- 2. PostgreSQL Migration (for production):
--    - Replace INTEGER PRIMARY KEY AUTOINCREMENT with SERIAL
--    - Add FOR UPDATE to SELECT queries in credit_manager.py
--    - Use row-level locking instead of database-level locking
--    - Add CHECK constraints for data integrity

-- 3. Future Enhancements:
--    - Add payment_history table to track EMI installments
--    - Add credit_limit_history to track limit changes over time
--    - Add utilization_alerts for users approaching limit
--    - Add affordability_overrides for manual approvals

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
