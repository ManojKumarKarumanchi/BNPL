"""Generate merchant master data for GrabOn BNPL system."""

import sqlite3
from typing import List, Dict
from config import GRABON_MERCHANTS


class MerchantGenerator:
    """Generates merchant master data from real GrabOn merchants."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_merchants_table(self, conn: sqlite3.Connection):
        """Create merchants table schema."""
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS merchants (
                merchant_id TEXT PRIMARY KEY,
                merchant_name TEXT NOT NULL,
                avg_discount_percent REAL,
                deal_count INTEGER DEFAULT 0,
                is_grabon_exclusive BOOLEAN DEFAULT 1
            )
        """)
        conn.commit()
        print("✅ Created merchants table")

    def generate_merchants(self, conn: sqlite3.Connection) -> int:
        """Insert real GrabOn merchants into database."""
        cursor = conn.cursor()

        for merchant in GRABON_MERCHANTS:
            cursor.execute("""
                INSERT INTO merchants (merchant_id, merchant_name, avg_discount_percent, deal_count, is_grabon_exclusive)
                VALUES (?, ?, ?, ?, ?)
            """, (
                merchant["id"],
                merchant["name"],
                merchant["avg_discount"],
                merchant["deal_count"],
                1  # All are GrabOn exclusive
            ))

        conn.commit()
        print(f"✅ Inserted {len(GRABON_MERCHANTS)} merchants")
        return len(GRABON_MERCHANTS)

    def run(self):
        """Execute merchant generation."""
        conn = sqlite3.connect(self.db_path)
        self.create_merchants_table(conn)
        count = self.generate_merchants(conn)
        conn.close()
        return count
