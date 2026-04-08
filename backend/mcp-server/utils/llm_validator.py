"""
LLM Output Validator - Prevents hallucinations in credit narratives.

Validates Azure OpenAI/Claude generated narratives against ground truth data
to ensure no incorrect credit limits or amounts are communicated to users.
"""

import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class LLMOutputValidator:
    """Validates LLM-generated narratives against ground truth data."""

    @staticmethod
    def extract_rupee_amounts(text: str) -> List[float]:
        """
        Extract all rupee amounts from text.

        Patterns matched:
        - ₹15,000 or ₹15000
        - Rs. 15,000 or Rs 15000
        - 15000 rupees or 15,000 rupees

        Args:
            text: Narrative text to parse

        Returns:
            List of extracted amounts as floats
        """
        patterns = [
            r'₹\s?([\d,]+)',           # ₹15,000 or ₹15000
            r'Rs\.?\s?([\d,]+)',       # Rs. 15,000 or Rs 15000
            r'([\d,]+)\s?rupees?'      # 15000 rupees
        ]

        amounts = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Remove commas and convert to float
                try:
                    amount = float(match.replace(',', ''))
                    amounts.append(amount)
                except ValueError:
                    continue

        return amounts

    @staticmethod
    def validate_narrative(
        narrative: str,
        ground_truth: Dict[str, float],
        tolerance: float = 0.01
    ) -> Tuple[bool, List[str]]:
        """
        Validate LLM narrative against ground truth values.

        Args:
            narrative: Generated narrative text
            ground_truth: Dict with keys: credit_limit, purchase_amount
            tolerance: Allowed variance (0.01 = 1%)

        Returns:
            (is_valid, list_of_errors)

        Examples:
            >>> validator = LLMOutputValidator()
            >>> narrative = "Approved for ₹25,000 credit limit"
            >>> truth = {'credit_limit': 15000, 'purchase_amount': 5000}
            >>> is_valid, errors = validator.validate_narrative(narrative, truth)
            >>> assert not is_valid
            >>> assert "Hallucinated amount: ₹25,000" in errors[0]
        """
        errors = []
        extracted_amounts = LLMOutputValidator.extract_rupee_amounts(narrative)

        if not extracted_amounts:
            # No amounts mentioned - this is acceptable
            # LLM may use descriptive language without exact figures
            return True, []

        # Get ground truth values
        credit_limit = ground_truth.get('credit_limit', 0)
        purchase_amount = ground_truth.get('purchase_amount', 0)

        # Validate each extracted amount
        for amount in extracted_amounts:
            is_valid_amount = False

            # Check against credit limit (with tolerance)
            if credit_limit > 0:
                relative_error = abs(amount - credit_limit) / credit_limit
                if relative_error <= tolerance:
                    is_valid_amount = True
                    continue

            # Check against purchase amount (with tolerance)
            if purchase_amount > 0:
                relative_error = abs(amount - purchase_amount) / purchase_amount
                if relative_error <= tolerance:
                    is_valid_amount = True
                    continue

            # Amount doesn't match any ground truth value
            if not is_valid_amount:
                errors.append(
                    f"Hallucinated amount: ₹{amount:,.0f} "
                    f"(expected ₹{credit_limit:,.0f} credit limit or "
                    f"₹{purchase_amount:,.0f} purchase amount)"
                )

        is_valid = len(errors) == 0

        if not is_valid:
            logger.warning(f"LLM validation failed: {'; '.join(errors)}")

        return is_valid, errors


def validate_and_retry_narrative(
    ai_client,
    prompt: str,
    ground_truth: Dict[str, float],
    max_retries: int = 2
) -> Tuple[str, bool]:
    """
    Generate narrative with validation and retry logic.

    This function ensures that LLM-generated narratives are grounded in actual
    credit decision data. If hallucination is detected, it retries up to
    max_retries times before returning the last attempt.

    Args:
        ai_client: AI client instance (Azure OpenAI or Claude)
        prompt: Prompt for narrative generation
        ground_truth: Ground truth values for validation
            - credit_limit: User's actual credit limit
            - purchase_amount: Actual purchase amount
        max_retries: Maximum retry attempts (default: 2)

    Returns:
        (narrative_text, is_validated)

    Usage:
        >>> from utils.claude_client import get_ai_client
        >>> ai_client = get_ai_client()
        >>> prompt = "Generate credit decision narrative..."
        >>> truth = {'credit_limit': 25000, 'purchase_amount': 12499}
        >>> narrative, is_valid = validate_and_retry_narrative(ai_client, prompt, truth)
        >>> if not is_valid:
        >>>     logger.error("Using unvalidated narrative - high hallucination risk")
    """
    validator = LLMOutputValidator()

    for attempt in range(max_retries + 1):
        try:
            # Generate narrative
            narrative = ai_client.generate_narrative(prompt, max_tokens=200)

            # Validate against ground truth
            is_valid, errors = validator.validate_narrative(narrative, ground_truth)

            if is_valid:
                if attempt > 0:
                    logger.warning(
                        f"Narrative validated after {attempt} retries "
                        f"(credit_limit=₹{ground_truth.get('credit_limit', 0):,.0f})"
                    )
                return narrative, True

            # Validation failed
            logger.warning(
                f"Attempt {attempt + 1}/{max_retries + 1}: "
                f"Narrative validation failed - {'; '.join(errors)}"
            )

        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed with error: {str(e)}")
            if attempt == max_retries:
                raise

    # All retries failed - return last narrative but flag as unvalidated
    logger.error(
        f"Failed to generate valid narrative after {max_retries} retries. "
        f"Ground truth: credit_limit=₹{ground_truth.get('credit_limit', 0):,.0f}, "
        f"purchase_amount=₹{ground_truth.get('purchase_amount', 0):,.0f}"
    )

    return narrative, False
