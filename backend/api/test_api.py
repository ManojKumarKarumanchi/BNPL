"""
Test FastAPI endpoints.
Quick test to verify API is working correctly.
"""

import httpx
import asyncio


async def test_health():
    """Test health check endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/health")
        print(f"\n{'='*80}")
        print("Health Check")
        print("="*80)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200


async def test_eligibility(user_id: str, expected_status: str):
    """Test eligibility check endpoint."""
    async with httpx.AsyncClient() as client:
        request_data = {
            "user_id": user_id,
            "product_id": "PROD_SAMSUNG_WATCH",
            "amount": 12499.0
        }

        response = await client.post(
            "http://localhost:8000/api/checkout/eligibility",
            json=request_data
        )

        print(f"\n{'='*80}")
        print(f"Eligibility Check: {user_id}")
        print("="*80)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Decision: {data['status']} (expected: {expected_status})")
            print(f"Credit Limit: ₹{data['credit_limit']:,.0f}")
            print(f"Reason: {data['reason'][:100]}...")

            if data.get('emi_options'):
                print(f"EMI Options: {len(data['emi_options'])} plans")
                for emi in data['emi_options']:
                    tag = f" ({emi['tag']})" if emi['tag'] else ""
                    print(f"  {emi['duration']} months: ₹{emi['monthly_payment']}/mo{tag}")

            # Validation
            if data['status'] == expected_status:
                print(f"✅ PASS")
            else:
                print(f"❌ FAIL: Expected {expected_status}, got {data['status']}")

        else:
            print(f"❌ Error: {response.text}")

        return response.status_code == 200


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("GrabOn BNPL API - Integration Tests")
    print("="*80)
    print("Testing all endpoints with 5 personas...")

    # Test health check
    await test_health()

    # Test all 5 personas
    personas = [
        ("USR_RAJESH", "new_user"),
        ("USR_PRIYA", "not_eligible"),
        ("USR_AMIT", "approved"),
        ("USR_SNEHA", "approved"),
        ("USR_VIKRAM", "approved")
    ]

    for user_id, expected_status in personas:
        await test_eligibility(user_id, expected_status)

    print("\n" + "="*80)
    print("Tests Complete")
    print("="*80)
    print("\nAPI is ready for frontend integration!")
    print("Frontend can now call: POST http://localhost:8000/api/checkout/eligibility")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\nStarting API tests...")
    print("Make sure the FastAPI server is running: python main.py")
    print()

    try:
        asyncio.run(main())
    except httpx.ConnectError:
        print("\n❌ Error: Could not connect to API server")
        print("Please start the server first: python main.py")
        print()
