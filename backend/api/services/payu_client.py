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
from config import settings

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
        self.base_url = settings.PAYU_SANDBOX_URL
        self.merchant_key = settings.PAYU_MERCHANT_KEY
        self.merchant_salt = settings.PAYU_MERCHANT_SALT
        self.mode = settings.PAYU_MODE

        # HTTP client with timeout
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=10.0,
            headers={
                "Content-Type": "application/json",
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

            # Prepare request payload
            payload = {
                "key": self.merchant_key,
                "txnid": txn_id,
                "amount": round(amount, 2),
                "productinfo": "GrabOn BNPL Purchase",
                "firstname": user_id.replace("USR_", ""),
                "email": email or f"{user_id.lower()}@grabon.in",
                "phone": mobile or "9999999999",  # Sandbox default
                "credit_limit": round(credit_limit, 2),
                "surl": f"{settings.API_BASE_URL}/api/payu/success",
                "furl": f"{settings.API_BASE_URL}/api/payu/failure",
                "service_provider": "lazypay",
                "mode": self.mode
            }

            # Generate hash
            hash_sequence = f"{self.merchant_key}|{txn_id}|{amount}|GrabOn BNPL Purchase|{user_id}"
            payload["hash"] = self._generate_hash(hash_sequence)

            # Call PayU LazyPay EMI Calculation API
            logger.info(f"Calling PayU LazyPay API for user {user_id}, amount ₹{amount}")

            response = await self.client.post(
                "/merchant/postservice.php?form=emi",
                json=payload
            )

            response.raise_for_status()
            data = response.json()

            # Parse PayU response
            if data.get("status") == "success":
                emi_plans = self._parse_emi_plans(data.get("emi_plans", []))

                logger.info(f"✅ PayU API success: {len(emi_plans)} EMI options for {user_id}")

                return {
                    "status": "success",
                    "emi_options": emi_plans,
                    "transaction_id": txn_id,
                    "error": None
                }
            else:
                error_msg = data.get("error", "Unknown PayU error")
                logger.warning(f"⚠️ PayU API returned error: {error_msg}")

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

        except Exception as e:
            logger.error(f"❌ PayU API unexpected error: {str(e)}")
            return {
                "status": "failure",
                "emi_options": [],
                "transaction_id": None,
                "error": f"PayU integration error: {str(e)}"
            }

    def _parse_emi_plans(self, raw_plans: List[Dict]) -> List[Dict[str, Any]]:
        """
        Parse PayU EMI plans into GrabOn BNPL format.

        PayU Format:
        {
            "tenure": 3,
            "monthly_installment": 4200.00,
            "interest_rate": 0,
            "total_amount": 12600.00,
            "processing_fee": 0
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

        for i, plan in enumerate(raw_plans, start=1):
            tenure = plan.get("tenure", 0)
            interest_rate = plan.get("interest_rate", 0)

            # Determine tag based on tenure and interest
            tag = None
            if interest_rate == 0:
                tag = "No Cost EMI"
            elif tenure == 6:
                tag = "Best Value"
            elif tenure == 9:
                tag = "VIP Rate"

            emi_options.append({
                "id": i,
                "duration": tenure,
                "monthly_payment": round(plan.get("monthly_installment", 0), 2),
                "tag": tag,
                "total_amount": round(plan.get("total_amount", 0), 2),
                "interest_rate": interest_rate,
                "processing_fee": round(plan.get("processing_fee", 0), 2),
                "provider": "PayU LazyPay"
            })

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


# Singleton instance
_payu_client: Optional[PayULazyPayClient] = None


def get_payu_client() -> PayULazyPayClient:
    """Get PayU LazyPay client singleton."""
    global _payu_client
    if _payu_client is None:
        _payu_client = PayULazyPayClient()
    return _payu_client
