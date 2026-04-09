"""
GrabOn BNPL Synthetic Data Generator
Entry point for generating realistic transaction data for 5 user personas.

Usage:
    python main.py
"""

import os
import sqlite3
import json
from datetime import datetime
from pathlib import Path

from config import ALL_PERSONAS, DB_PATH
from generators.merchant_generator import MerchantGenerator
from generators.user_generator import UserGenerator
from generators.transaction_generator import TransactionGenerator


def setup_database():
    """Create output directory and initialize database."""
    # Create output directory
    output_dir = Path(DB_PATH).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Remove old database if exists
    if os.path.exists(DB_PATH):
        print(f"🗑️  Removing old database: {DB_PATH}")
        os.remove(DB_PATH)

    print(f"📁 Database path: {DB_PATH}\n")


def generate_report(db_path: str):
    """Generate summary report of generated data."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get summary stats
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM merchants")
    merchant_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM transactions")
    transaction_count = cursor.fetchone()[0]

    # Get per-user stats
    cursor.execute("""
        SELECT
            u.user_id,
            u.name,
            COUNT(t.transaction_id) as txn_count,
            COALESCE(AVG(t.final_amount), 0) as avg_order,
            COALESCE(SUM(CASE WHEN t.is_returned = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 0) as return_rate,
            COALESCE(SUM(CASE WHEN t.coupon_used IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 0) as coupon_rate
        FROM users u
        LEFT JOIN transactions t ON u.user_id = t.user_id
        GROUP BY u.user_id, u.name
        ORDER BY txn_count DESC
    """)

    user_stats = cursor.fetchall()

    conn.close()

    # Create report
    report = {
        "generation_timestamp": datetime.now().isoformat(),
        "database_path": db_path,
        "summary": {
            "total_users": user_count,
            "total_merchants": merchant_count,
            "total_transactions": transaction_count
        },
        "user_personas": [
            {
                "user_id": row[0],
                "name": row[1],
                "transactions": row[2],
                "avg_order_value": round(row[3], 2),
                "return_rate": round(row[4], 2),
                "coupon_redemption_rate": round(row[5], 2)
            }
            for row in user_stats
        ]
    }

    # Save report
    report_path = Path(db_path).parent / "generation_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Generation report saved: {report_path}")

    return report


def print_summary(report: dict):
    """Print formatted summary of generated data."""
    print("\n" + "=" * 80)
    print("📊 SYNTHETIC DATA GENERATION SUMMARY")
    print("=" * 80)

    summary = report["summary"]
    print(f"\n✅ Total Users: {summary['total_users']}")
    print(f"✅ Total Merchants: {summary['total_merchants']}")
    print(f"✅ Total Transactions: {summary['total_transactions']}")

    print("\n👥 User Persona Breakdown:")
    print("-" * 80)
    print(f"{'Name':<20} {'User ID':<15} {'Txns':<8} {'Avg Order':<12} {'Return %':<10} {'Coupon %'}")
    print("-" * 80)

    for user in report["user_personas"]:
        print(f"{user['name']:<20} {user['user_id']:<15} {user['transactions']:<8} "
            f"₹{user['avg_order_value']:<10,.2f} {user['return_rate']:<9.1f}% {user['coupon_redemption_rate']:.1f}%")

    print("-" * 80)
    print(f"\n✅ Database created: {report['database_path']}")
    print(f"⏰ Generated at: {report['generation_timestamp']}")
    print("=" * 80)


def main():
    """Main execution function."""
    print("\n" + "=" * 80)
    print("GrabOn BNPL Synthetic Data Generator")
    print("=" * 80)
    print("Generating realistic transaction data for 5 user personas...")
    print()

    # Setup
    setup_database()

    # Step 1: Generate Merchants
    print("📦 Step 1: Generating Merchants")
    print("-" * 80)
    merchant_gen = MerchantGenerator(DB_PATH)
    merchant_count = merchant_gen.run()

    # Step 2: Generate Users
    print("\n👤 Step 2: Generating Users")
    print("-" * 80)
    user_gen = UserGenerator(DB_PATH)
    user_count = user_gen.run()

    # Step 3: Generate Transactions
    print("\n💳 Step 3: Generating Transactions")
    print("-" * 80)
    transaction_gen = TransactionGenerator(DB_PATH)
    transaction_count = transaction_gen.run(ALL_PERSONAS)

    # Step 4: Generate Report
    print("\n📋 Step 4: Generating Report")
    print("-" * 80)
    report = generate_report(DB_PATH)

    # Print Summary
    print_summary(report)

    print("\n✅ Data generation complete! Ready for MCP server integration.")
    print(f"💡 Next step: cd ../mcp-server && python server.py")
    print()


if __name__ == "__main__":
    main()
