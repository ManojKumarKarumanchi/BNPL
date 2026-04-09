"""
Generate realistic transaction data using Evidently AI synthetic data generators.
References:
- https://www.evidentlyai.com/blog/synthetic-data-generator-python
- https://github.com/evidentlyai/evidently/blob/main/examples/cookbook/datagen.ipynb
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict
from faker import Faker

from config import (
    PersonaConfig,
    GRABON_MERCHANTS,
    GRABON_CATEGORIES,
    PAYMENT_MODES,
    COUPON_CODES
)

fake = Faker('en_IN')  # Indian locale for realistic data


class TransactionGenerator:
    """Generates synthetic transactions using realistic distributions."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_transactions_table(self, conn: sqlite3.Connection):
        """Create transactions table schema."""
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
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
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)")

        conn.commit()
        print("✅ Created transactions table with indexes")

    def generate_transaction_dates(self, persona: PersonaConfig, count: int) -> List[datetime]:
        """Generate realistic transaction dates with temporal patterns."""
        if count == 0:
            return []

        member_since = persona.member_since
        days_active = (datetime.now() - member_since).days

        if days_active <= 0:
            return []  # New user, no transactions yet

        # Generate dates with clustering (weekends, paydays)
        dates = []
        current_date = member_since

        # Distribute transactions over active period
        days_between = max(1, days_active // count)

        for i in range(count):
            # Add some randomness (±3 days)
            jitter = np.random.randint(-3, 4)
            date = current_date + timedelta(days=i * days_between + jitter)

            # Ensure date doesn't exceed today
            if date > datetime.now():
                date = datetime.now() - timedelta(days=np.random.randint(0, 7))

            dates.append(date)

        # Sort dates chronologically
        return sorted(dates)

    def select_category(self, persona: PersonaConfig) -> str:
        """Select category based on persona preferences."""
        if not persona.category_preferences:
            # Equal distribution for new users
            categories = [cat["name"] for cat in GRABON_CATEGORIES]
            return np.random.choice(categories)

        categories = list(persona.category_preferences.keys())
        probabilities = list(persona.category_preferences.values())

        return np.random.choice(categories, p=probabilities)

    def select_merchant(self, persona: PersonaConfig) -> str:
        """Select merchant based on persona preferences."""
        if not persona.merchant_preferences:
            # Weighted by deal_count for new users
            merchant_ids = [m["id"] for m in GRABON_MERCHANTS]
            deal_counts = [m["deal_count"] for m in GRABON_MERCHANTS]
            probabilities = np.array(deal_counts) / sum(deal_counts)
            return np.random.choice(merchant_ids, p=probabilities)

        merchant_ids = list(persona.merchant_preferences.keys())
        probabilities = list(persona.merchant_preferences.values())

        return np.random.choice(merchant_ids, p=probabilities)

    def generate_order_value(self, persona: PersonaConfig, category: str) -> float:
        """Generate order value using log-normal distribution."""
        # Base on persona's average order value
        mean = persona.avg_order_value if persona.avg_order_value > 0 else 1500
        std = mean * 0.6  # 60% standard deviation for variety

        # Log-normal distribution (realistic for e-commerce)
        value = np.random.lognormal(np.log(mean), 0.5)

        # Category-specific adjustments
        if category == "Travel":
            value *= 3.0  # Travel is more expensive
        elif category == "Electronics":
            value *= 1.5
        elif category == "Food":
            value *= 0.5  # Food is cheaper

        # Clamp to realistic range (₹99 to ₹99,999)
        value = max(99, min(99999, value))

        return round(value, 2)

    def apply_discount(self, order_value: float, merchant_id: str) -> float:
        """Apply merchant-specific discount."""
        merchant = next((m for m in GRABON_MERCHANTS if m["id"] == merchant_id), None)
        if not merchant:
            return 0

        # Discount percentage from merchant config
        discount_pct = merchant["avg_discount"]

        # Add randomness (±10%)
        actual_discount_pct = discount_pct + np.random.uniform(-10, 10)
        actual_discount_pct = max(0, min(95, actual_discount_pct))  # Clamp 0-95%

        discount_amount = order_value * (actual_discount_pct / 100)
        return round(discount_amount, 2)

    def should_use_coupon(self, persona: PersonaConfig) -> bool:
        """Determine if coupon should be used based on redemption rate."""
        return np.random.random() < persona.coupon_redemption_rate

    def should_return(self, persona: PersonaConfig) -> bool:
        """Determine if transaction should be returned based on return rate."""
        return np.random.random() < persona.return_rate

    def generate_transactions_for_persona(
        self,
        persona: PersonaConfig
    ) -> List[Dict]:
        """Generate all transactions for a single persona."""
        if persona.total_purchases == 0:
            print(f"  ⏭️  {persona.name}: Skipping (new user with 0 transactions)")
            return []

        print(f"  🔄 Generating {persona.total_purchases} transactions for {persona.name}...")

        transactions = []
        dates = self.generate_transaction_dates(persona, persona.total_purchases)

        for i, date in enumerate(dates):
            # Select category and merchant
            category = self.select_category(persona)
            merchant_id = self.select_merchant(persona)

            # Generate order value
            order_value = self.generate_order_value(persona, category)

            # Apply discount
            discount_amount = self.apply_discount(order_value, merchant_id)
            final_amount = order_value - discount_amount

            # Coupon usage
            coupon_used = None
            if self.should_use_coupon(persona):
                coupon_used = np.random.choice(COUPON_CODES)

            # Payment mode
            payment_mode = np.random.choice(PAYMENT_MODES)

            # Return flag
            is_returned = self.should_return(persona)

            transaction = {
                "transaction_id": f"TXN_{persona.user_id}_{i+1:04d}",
                "user_id": persona.user_id,
                "merchant_id": merchant_id,
                "category": category,
                "order_value": order_value,
                "discount_amount": discount_amount,
                "final_amount": final_amount,
                "coupon_used": coupon_used,
                "payment_mode": payment_mode,
                "is_returned": 1 if is_returned else 0,
                "transaction_date": date.strftime("%Y-%m-%d")
            }

            transactions.append(transaction)

        return transactions

    def insert_transactions(self, conn: sqlite3.Connection, transactions: List[Dict]):
        """Bulk insert transactions into database."""
        cursor = conn.cursor()

        cursor.executemany("""
            INSERT INTO transactions (
                transaction_id, user_id, merchant_id, category,
                order_value, discount_amount, final_amount,
                coupon_used, payment_mode, is_returned, transaction_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (
                txn["transaction_id"],
                txn["user_id"],
                txn["merchant_id"],
                txn["category"],
                txn["order_value"],
                txn["discount_amount"],
                txn["final_amount"],
                txn["coupon_used"],
                txn["payment_mode"],
                txn["is_returned"],
                txn["transaction_date"]
            )
            for txn in transactions
        ])

        conn.commit()

    def validate_persona_data(self, conn: sqlite3.Connection, persona: PersonaConfig):
        """Validate generated data matches persona specs."""
        cursor = conn.cursor()

        # Check transaction count
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE user_id = ?", (persona.user_id,))
        actual_count = cursor.fetchone()[0]

        # Check average order value
        cursor.execute("SELECT AVG(final_amount) FROM transactions WHERE user_id = ?", (persona.user_id,))
        actual_avg = cursor.fetchone()[0] or 0

        # Check return rate
        cursor.execute("""
            SELECT
                SUM(CASE WHEN is_returned = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as return_pct
            FROM transactions
            WHERE user_id = ?
        """, (persona.user_id,))
        actual_return_rate = cursor.fetchone()[0] or 0

        # Print validation results
        print(f"\n  ✅ {persona.name} validation:")
        print(f"     Transactions: {actual_count} (expected: {persona.total_purchases})")
        print(f"     Avg Order Value: ₹{actual_avg:,.2f} (expected: ₹{persona.avg_order_value:,.2f})")
        print(f"     Return Rate: {actual_return_rate:.1f}% (expected: {persona.return_rate*100:.1f}%)")

    def run(self, personas: List[PersonaConfig]):
        """Execute transaction generation for all personas."""
        conn = sqlite3.connect(self.db_path)
        self.create_transactions_table(conn)

        all_transactions = []

        print("\n🔄 Generating transactions for all personas...")
        print("=" * 80)

        for persona in personas:
            transactions = self.generate_transactions_for_persona(persona)
            all_transactions.extend(transactions)

        # Bulk insert all transactions
        if all_transactions:
            print(f"\n💾 Inserting {len(all_transactions)} transactions into database...")
            self.insert_transactions(conn, all_transactions)

        # Validate each persona
        print("\n📊 Validating generated data...")
        print("=" * 80)
        for persona in personas:
            if persona.total_purchases > 0:
                self.validate_persona_data(conn, persona)

        conn.close()
        return len(all_transactions)
