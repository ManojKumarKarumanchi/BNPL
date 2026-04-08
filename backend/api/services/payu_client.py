"""
PayU LazyPay API Client
Integrates with PayU LazyPay sandbox for BNPL disbursal flow.

API Reference: PayU LazyPay Sandbox v2
https://docs.payu.in/docs/lazypay-integration
"""

import hashlib
import httpx
import logging
from typing import Dict, List, Any, Optional
from api.config import settings

logger = logging.getLogger(__name__)


class PayULazyPayClient:
    """
    PayU LazyPay sandbox API client for BNPL integration.

    Implements:
    - EMI offer calculation
    - Checkout initiation
    - Transaction status check
    """

    def __init__(self):
        # Use PayU API URL from settings
        self.base_url = settings.PAYU_SANDBOX_URL
        self.merchant_key = settings.PAYU_MERCHANT_KEY
        self.merchant_salt = settings.PAYU_MERCHANT_SALT
        self.mode = settings.PAYU_MODE

        # HTTP client with timeout
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=10.0,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",  # PayU uses form data
                "Accept": "application/json"
            }
        )

    def _generate_hash(self, data: str) -> str:
        """
        Generate SHA512 hash for PayU authentication.

        Formula: sha512(key|txnid|amount|productinfo|firstname|email|udf1|...|salt)
        """
        hash_string = f"{data}|{self.merchant_salt}"
        return hashlib.sha512(hash_string.encode('utf-8')).hexdigest()

    async def calculate_emi_offers(
        self,
        user_id: str,
        amount: float,
        credit_limit: float,
        mobile: Optional[str] = None,
        email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Call PayU LazyPay API to calculate EMI offers.

        Args:
            user_id: GrabOn user ID
            amount: Purchase amount
            credit_limit: User's approved credit limit
            mobile: User mobile number (optional for sandbox)
            email: User email (optional for sandbox)

        Returns:
            {
                "status": "success" | "failure",
                "emi_options": List[Dict],
                "transaction_id": str,
                "error": Optional[str]
            }
        """
        try:
            # Generate transaction ID
            import uuid
            txn_id = f"GRABON_{user_id}_{uuid.uuid4().hex[:8]}"

            # Prepare request payload (PayU uses form-encoded data)
            # Using official PayU EMI Calculator API endpoint
            firstname = user_id.replace("USR_", "")
            user_email = email or f"{user_id.lower()}@grabon.in"

            # PayU hash formula: key|txnid|amount|productinfo|firstname|email|||||||||||salt
            hash_string = f"{self.merchant_key}|{txn_id}|{amount}|GrabOn BNPL Purchase|{firstname}|{user_email}|||||||||||{self.merchant_salt}"
            hash_value = hashlib.sha512(hash_string.encode('utf-8')).hexdigest()

            payload = {
                "key": self.merchant_key,
                "txnid": txn_id,
                "amount": str(round(amount, 2)),
                "productinfo": "GrabOn BNPL Purchase",
                "firstname": firstname,
                "email": user_email,
                "phone": mobile or "9999999999",
                "surl": f"{settings.API_BASE_URL}/api/payu/success",
                "furl": f"{settings.API_BASE_URL}/api/payu/failure",
                "hash": hash_value,
                "service_provider": "payu_paisa"
            }

            # Call PayU EMI Calculation API (form=2 is for EMI details)
            logger.info(f"🔗 Calling PayU EMI API for user {user_id}, amount ₹{amount}")

            response = await self.client.post(
                "/merchant/postservice?form=2",
                data=payload  # Use form data, not JSON
            )

            response.raise_for_status()

            # Check if response is JSON
            content_type = response.headers.get('content-type', '')
            if 'json' not in content_type.lower():
                logger.warning(f"⚠️ PayU API returned non-JSON response: {content_type}")
                logger.debug(f"Response body: {response.text[:200]}")
                return {
                    "status": "failure",
                    "emi_options": [],
                    "transaction_id": txn_id,
                    "error": "PayU API returned non-JSON response"
                }

            data = response.json()

            # PayU EMI API returns: {"status": 1, "result": {...}, "emi_details": {...}}
            if data.get("status") == 1 or data.get("status") == "1":
                # Extract EMI details from response
                emi_details = data.get("emi_details", {})
                emi_plans = self._parse_payu_emi_response(emi_details, amount)

                if emi_plans:
                    logger.info(f"✅ PayU API success: {len(emi_plans)} EMI options for {user_id}")
                    return {
                        "status": "success",
                        "emi_options": emi_plans,
                        "transaction_id": txn_id,
                        "error": None
                    }
                else:
                    logger.warning(f"⚠️ PayU API returned no EMI plans")
                    return {
                        "status": "failure",
                        "emi_options": [],
                        "transaction_id": txn_id,
                        "error": "No EMI plans available from PayU"
                    }
            else:
                error_msg = data.get("msg", data.get("error", "Unknown PayU error"))
                logger.warning(f"⚠️ PayU API error: {error_msg}")
                return {
                    "status": "failure",
                    "emi_options": [],
                    "transaction_id": txn_id,
                    "error": error_msg
                }

        except httpx.TimeoutException:
            logger.error("❌ PayU API timeout")
            return {
                "status": "failure",
                "emi_options": [],
                "transaction_id": None,
                "error": "PayU API timeout"
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ PayU API HTTP error: {e.response.status_code}")
            return {
                "status": "failure",
                "emi_options": [],
                "transaction_id": None,
                "error": f"PayU API error: {e.response.status_code}"
            }

        except httpx.JSONDecodeError as e:
            logger.error(f"❌ PayU API returned invalid JSON: {str(e)}")
            logger.debug(f"Response text: {response.text[:500] if 'response' in locals() else 'N/A'}")
            return {
                "status": "failure",
                "emi_options": [],
                "transaction_id": None,
                "error": "PayU API returned invalid response format"
            }

        except Exception as e:
            logger.error(f"❌ PayU API unexpected error: {str(e)}")
            return {
                "status": "failure",
                "emi_options": [],
                "transaction_id": None,
                "error": f"PayU integration error: {str(e)}"
            }

    def _parse_payu_emi_response(self, emi_details: Dict, amount: float) -> List[Dict[str, Any]]:
        """
        Parse PayU EMI response into GrabOn BNPL format.

        PayU EMI API returns nested structure with bank-wise EMI details:
        {
            "BANK_CODE": {
                "3": {"monthly_installment": 4200, "interest_rate": 0, ...},
                "6": {"monthly_installment": 2100, "interest_rate": 2.5, ...}
            }
        }

        GrabOn Format:
        {
            "id": 1,
            "duration": 3,
            "monthly_payment": 4200.00,
            "tag": "No Cost EMI",
            "total_amount": 12600.00,
            "interest_rate": 0
        }
        """
        emi_options = []
        plan_id = 1

        # Iterate through all banks and their EMI plans
        for bank_code, plans in emi_details.items():
            if not isinstance(plans, dict):
                continue

            for tenure_str, plan_data in plans.items():
                try:
                    tenure = int(tenure_str)

                    # Extract EMI details
                    monthly_emi = float(plan_data.get("emi_amount", plan_data.get("monthly_installment", 0)))
                    interest_rate = float(plan_data.get("interest_rate", 0))

                    # Calculate total amount
                    total_amount = monthly_emi * tenure

                    # Determine tag based on tenure and interest
                    tag = None
                    if interest_rate == 0:
                        tag = "No Cost EMI"
                    elif tenure == 6:
                        tag = "Best Value"
                    elif tenure == 9:
                        tag = "VIP Rate"

                    emi_options.append({
                        "id": plan_id,
                        "duration": tenure,
                        "monthly_payment": round(monthly_emi, 2),
                        "tag": tag,
                        "total_amount": round(total_amount, 2),
                        "interest_rate": interest_rate,
                        "processing_fee": 0.0,
                        "provider": "PayU LazyPay"
                    })

                    plan_id += 1

                except (ValueError, TypeError) as e:
                    logger.debug(f"Skipping invalid EMI plan: {e}")
                    continue

        # If no plans found, try simpler format (some PayU responses vary)
        if not emi_options and isinstance(emi_details, list):
            for i, plan in enumerate(emi_details, start=1):
                try:
                    tenure = int(plan.get("tenure", plan.get("duration", 0)))
                    monthly_emi = float(plan.get("monthly_installment", plan.get("emi_amount", 0)))
                    interest_rate = float(plan.get("interest_rate", 0))

                    tag = "No Cost EMI" if interest_rate == 0 else None

                    emi_options.append({
                        "id": i,
                        "duration": tenure,
                        "monthly_payment": round(monthly_emi, 2),
                        "tag": tag,
                        "total_amount": round(monthly_emi * tenure, 2),
                        "interest_rate": interest_rate,
                        "processing_fee": 0.0,
                        "provider": "PayU LazyPay"
                    })
                except (ValueError, TypeError, KeyError):
                    continue

        # Sort by duration (shortest first)
        emi_options.sort(key=lambda x: x["duration"])

        return emi_options

    async def initiate_checkout(
        self,
        transaction_id: str,
        emi_duration: int,
        user_id: str,
        amount: float
    ) -> Dict[str, Any]:
        """
        Initiate BNPL checkout flow with PayU LazyPay.

        Args:
            transaction_id: PayU transaction ID
            emi_duration: Selected EMI duration (months)
            user_id: GrabOn user ID
            amount: Purchase amount

        Returns:
            {
                "status": "success" | "failure",
                "checkout_url": str,  # PayU checkout page URL
                "mihpayid": str,  # PayU payment ID
                "error": Optional[str]
            }
        """
        try:
            payload = {
                "key": self.merchant_key,
                "txnid": transaction_id,
                "amount": round(amount, 2),
                "emi_duration": emi_duration,
                "productinfo": "GrabOn BNPL Purchase",
                "firstname": user_id.replace("USR_", ""),
                "service_provider": "lazypay"
            }

            # Generate hash
            hash_sequence = f"{self.merchant_key}|{transaction_id}|{amount}|GrabOn BNPL Purchase"
            payload["hash"] = self._generate_hash(hash_sequence)

            response = await self.client.post(
                "/merchant/paymentgateway.php",
                json=payload
            )

            response.raise_for_status()
            data = response.json()

            if data.get("status") == "success":
                return {
                    "status": "success",
                    "checkout_url": data.get("payment_url"),
                    "mihpayid": data.get("mihpayid"),
                    "error": None
                }
            else:
                return {
                    "status": "failure",
                    "checkout_url": None,
                    "mihpayid": None,
                    "error": data.get("error", "Checkout initiation failed")
                }

        except Exception as e:
            logger.error(f"❌ PayU checkout error: {str(e)}")
            return {
                "status": "failure",
                "checkout_url": None,
                "mihpayid": None,
                "error": f"Checkout error: {str(e)}"
            }

    async def check_transaction_status(
        self,
        transaction_id: str
    ) -> Dict[str, Any]:
        """
        Check PayU transaction status.

        Args:
            transaction_id: PayU transaction ID

        Returns:
            {
                "status": "success" | "pending" | "failed",
                "amount": float,
                "bank_ref_num": str,
                "error": Optional[str]
            }
        """
        try:
            payload = {
                "key": self.merchant_key,
                "command": "verify_payment",
                "var1": transaction_id
            }

            hash_sequence = f"{self.merchant_key}|verify_payment|{transaction_id}"
            payload["hash"] = self._generate_hash(hash_sequence)

            response = await self.client.post(
                "/merchant/postservice.php?form=verify",
                json=payload
            )

            response.raise_for_status()
            data = response.json()

            return {
                "status": data.get("transaction_details", {}).get("status", "unknown"),
                "amount": data.get("transaction_details", {}).get("amount", 0),
                "bank_ref_num": data.get("transaction_details", {}).get("bank_ref_num"),
                "error": None
            }

        except Exception as e:
            logger.error(f"❌ Status check error: {str(e)}")
            return {
                "status": "unknown",
                "amount": 0,
                "bank_ref_num": None,
                "error": f"Status check failed: {str(e)}"
            }

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


class MockPayUClient:
    """
    Mock PayU LazyPay client for demo/testing without real credentials.

    ALIGNED WITH ACTUAL PayU LazyPay TERMS:
    - 15-day @ 0% interest (primary offering)
    - 3/6/9/12-month EMI with 12-18% p.a. interest
    - Credit limits: ₹10K-₹100K
    - Lending partners: RBL Bank / DMI Finance

    Strategic Partnership Context:
    GrabOn has a strategic partnership with PayU (India's leading payment
    infrastructure) to offer PayU LazyPay as the BNPL product for GrabCredit.
    This mock client uses actual PayU LazyPay terms for demo purposes.

    Returns realistic PayU-format responses without calling external API.
    Useful for:
    - Local development without merchant credentials
    - Automated testing
    - Demo environments with actual PayU LazyPay terms
    """

    def __init__(self):
        logger.info("🎭 MockPayUClient initialized (PayU LazyPay actual terms, no real API calls)")

    async def calculate_emi_offers(
        self,
        user_id: str,
        amount: float,
        credit_limit: float,
        mobile: Optional[str] = None,
        email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mock EMI calculation - returns realistic PayU-format response.

        Simulates PayU EMI API without network calls.
        """
        import uuid
        txn_id = f"MOCK_GRABON_{user_id}_{uuid.uuid4().hex[:8]}"

        logger.info(f"🎭 [MOCK PayU] Calculating EMI for {user_id}, amount ₹{amount}")

        # Simulate PayU LazyPay EMI plans (ACTUAL PayU LazyPay terms)
        # Primary: 15-day @ 0% (duration 0.5)
        # Secondary: 3/6/9/12 month EMI @ 12-18% p.a.
        from datetime import datetime, timedelta

        mock_emi_details = {
            "LAZYPAY": {
                "0.5": {  # 15-day one-time payment (PayU LazyPay primary)
                    "emi_amount": amount,  # Full amount
                    "interest_rate": 0.0,
                    "bank_interest": 0.0,
                    "bank_name": "PayU LazyPay",
                    "due_date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
                    "is_one_time_payment": True
                },
                "3": {
                    "emi_amount": round(amount / 3 * 1.03, 2),  # 12% annual = 3% for 3 months
                    "interest_rate": 12.0,  # PayU actual rate
                    "bank_interest": round(amount * 0.03, 2),
                    "bank_name": "RBL Bank"  # PayU lending partner
                },
                "6": {
                    "emi_amount": round(amount / 6 * 1.07, 2),  # 14% annual = 7% for 6 months
                    "interest_rate": 14.0,
                    "bank_interest": round(amount * 0.07, 2),
                    "bank_name": "RBL Bank"
                }
            },
            "DMI_FINANCE": {
                "9": {
                    "emi_amount": round(amount / 9 * 1.12, 2),  # 16% annual = 12% for 9 months
                    "interest_rate": 16.0,
                    "bank_interest": round(amount * 0.12, 2),
                    "bank_name": "DMI Finance"  # PayU NBFC partner
                },
                "12": {
                    "emi_amount": round(amount / 12 * 1.18, 2),  # 18% annual
                    "interest_rate": 18.0,
                    "bank_interest": round(amount * 0.18, 2),
                    "bank_name": "DMI Finance"
                }
            }
        }

        # Filter plans based on credit tier (PayU LazyPay actual business rules)
        # Growing tier (₹10K limit): 15-day, 3, 6 months
        # Regular tier (₹30K limit): 15-day, 3, 6, 9 months
        # Power tier (₹100K limit): all tenures including 12 months
        if credit_limit <= 10000:
            # Remove 9 and 12 month plans
            mock_emi_details.pop("DMI_FINANCE", None)
        elif credit_limit <= 30000:
            # Remove 12 month plan only
            if "DMI_FINANCE" in mock_emi_details:
                mock_emi_details["DMI_FINANCE"].pop("12", None)

        # Parse mock response using same logic as real PayU
        emi_plans = self._parse_payu_emi_response(mock_emi_details, amount)

        logger.info(f"✅ [MOCK PayU] Generated {len(emi_plans)} EMI options for {user_id}")

        return {
            "status": "success",
            "emi_options": emi_plans,
            "transaction_id": txn_id,
            "error": None
        }

    def _parse_payu_emi_response(self, emi_details: Dict, amount: float) -> List[Dict[str, Any]]:
        """
        Parse PayU EMI response - same as real client.
        """
        emi_options = []
        plan_id = 1

        for bank_code, plans in emi_details.items():
            if not isinstance(plans, dict):
                continue

            for tenure_str, plan_data in plans.items():
                try:
                    tenure = int(tenure_str)
                    monthly_emi = float(plan_data.get("emi_amount", plan_data.get("monthly_installment", 0)))
                    interest_rate = float(plan_data.get("interest_rate", 0))
                    total_amount = monthly_emi * tenure

                    tag = None
                    if interest_rate == 0:
                        tag = "No Cost EMI"
                    elif tenure == 6:
                        tag = "Best Value"
                    elif tenure == 9:
                        tag = "VIP Rate"

                    emi_options.append({
                        "id": plan_id,
                        "duration": tenure,
                        "monthly_payment": round(monthly_emi, 2),
                        "tag": tag,
                        "total_amount": round(total_amount, 2),
                        "interest_rate": interest_rate,
                        "processing_fee": 0.0,
                        "provider": "PayU LazyPay",  # PayU strategic partner
                        "is_one_time_payment": plan_data.get("is_one_time_payment", False),
                        "due_date": plan_data.get("due_date")  # For 15-day payment
                    })

                    plan_id += 1

                except (ValueError, TypeError) as e:
                    logger.debug(f"Skipping invalid EMI plan: {e}")
                    continue

        emi_options.sort(key=lambda x: x["duration"])
        return emi_options

    async def initiate_checkout(
        self,
        transaction_id: str,
        emi_duration: int,
        user_id: str,
        amount: float
    ) -> Dict[str, Any]:
        """Mock checkout initiation."""
        logger.info(f"🎭 [MOCK PayU] Checkout initiated: {transaction_id}")
        return {
            "status": "success",
            "checkout_url": f"https://mock-payu.grabon.in/checkout/{transaction_id}",
            "mihpayid": f"MOCK_MIHPAY_{transaction_id}",
            "error": None
        }

    async def check_transaction_status(
        self,
        transaction_id: str
    ) -> Dict[str, Any]:
        """Mock transaction status check."""
        logger.info(f"🎭 [MOCK PayU] Status check: {transaction_id}")
        return {
            "status": "success",
            "amount": 12499.0,
            "bank_ref_num": f"MOCK_BANK_REF_{transaction_id}",
            "error": None
        }

    async def close(self):
        """No-op for mock client."""
        pass


# Factory pattern for PayU client selection
_payu_client: Optional[PayULazyPayClient] = None
_mock_payu_client: Optional[MockPayUClient] = None


def get_payu_client():
    """
    Get PayU client (real or mock) based on configuration.

    Returns MockPayUClient if:
    - PAYU_ENABLED=false (explicit disable)
    - PAYU_MERCHANT_KEY is default/test value (no real credentials)

    Returns real PayULazyPayClient if:
    - PAYU_ENABLED=true AND valid merchant credentials provided

    This allows seamless development without PayU merchant account.
    """
    global _payu_client, _mock_payu_client

    # Check if real PayU credentials are configured
    has_real_credentials = (
        settings.PAYU_ENABLED and
        settings.PAYU_MERCHANT_KEY not in ["gtKFFx", "", None] and  # Not default/empty
        settings.PAYU_MERCHANT_SALT not in ["4R38IvwiV57FwVpsgOvTXBdLE4tHUXFW", "", None]
    )

    if has_real_credentials:
        # Use real PayU client
        if _payu_client is None:
            logger.info("🔗 Initializing REAL PayU LazyPay client")
            _payu_client = PayULazyPayClient()
        return _payu_client
    else:
        # Use mock PayU client
        if _mock_payu_client is None:
            logger.info("🎭 Initializing MOCK PayU client (no real credentials)")
            _mock_payu_client = MockPayUClient()
        return _mock_payu_client
