"""Generate user profiles for 5 GrabOn BNPL personas."""

import sqlite3
from typing import List
from config import ALL_PERSONAS


class UserGenerator:
    """Generates user profiles matching frontend personas."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_users_table(self, conn: sqlite3.Connection):
        """Create users table schema."""
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                member_since DATE NOT NULL,
                account_status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("✅ Created users table")

    def generate_users(self, conn: sqlite3.Connection) -> int:
        """Insert 5 persona users into database."""
        cursor = conn.cursor()

        for persona in ALL_PERSONAS:
            cursor.execute("""
                INSERT INTO users (user_id, name, email, member_since, account_status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                persona.user_id,
                persona.name,
                persona.email,
                persona.member_since.strftime("%Y-%m-%d"),
                'active'
            ))

        conn.commit()
        print(f"✅ Inserted {len(ALL_PERSONAS)} users")

        # Print user summary
        print("\n📊 User Persona Summary:")
        print("=" * 80)
        for persona in ALL_PERSONAS:
            print(f"{persona.name:20} | {persona.user_id:12} | {persona.credit_tier:10} | "
                  f"{persona.total_purchases:3} txns | ₹{persona.avg_order_value:,.0f} avg")
        print("=" * 80)

        return len(ALL_PERSONAS)

    def run(self):
        """Execute user generation."""
        conn = sqlite3.connect(self.db_path)
        self.create_users_table(conn)
        count = self.generate_users(conn)
        conn.close()
        return count
