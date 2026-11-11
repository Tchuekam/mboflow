"""
Cameroonian Mobile Money (MTN MoMo & Orange Money) SMS & Receipt Parser.
Extracts amounts, fees, balances, references, and deterministically validates:
Previous Balance - (Amount + Fee) == New Balance.
"""

import re
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from packages.financial_validation.validator import DeterministicFinancialValidator
from packages.shared_schemas.mboa_schemas import VerificationStatus


class ParsedMobileMoneySMS(BaseModel):
    provider: str  # MTN_MOMO, ORANGE_MONEY, EXPRESS_UNION, UNKNOWN
    transaction_type: str  # TRANSFER, CASH_IN, CASH_OUT, PAYMENT
    amount: float
    fee: float
    total_deducted: float
    new_balance: Optional[float] = None
    recipient_or_sender: Optional[str] = None
    transaction_reference: Optional[str] = None
    currency: str = "FCFA"
    is_mathematically_consistent: bool = True
    discrepancy_amount: float = 0.0
    notes: List[str] = []


class MobileMoneySMSParser:
    """
    Deterministic SMS parser for Cameroonian Mobile Money receipts and notifications.
    """

    MTN_PATTERN = re.compile(r'transfert\s+de\s+(.*?)\s+(?:effectu[eé]|au)\s+(\d{9})', re.IGNORECASE)
    ORANGE_PATTERN = re.compile(r'transf[eé]r[eé]\s+(.*?)\s+[aà]\s+(\d{9})', re.IGNORECASE)
    REF_PATTERN = re.compile(r'(?:ID|R[eé]f|TxID)[:\s]+([A-Z0-9.\-_]{8,24})', re.IGNORECASE)

    @classmethod
    def parse_sms(cls, sms_text: str, previous_balance: Optional[float] = None) -> ParsedMobileMoneySMS:
        """
        Parses raw SMS text from MTN Mobile Money or Orange Money Cameroon.
        """
        text_lower = sms_text.lower()
        provider = "UNKNOWN"
        if "mtn" in text_lower or "momo" in text_lower or "67" in text_lower or "68" in text_lower or "650" in text_lower or "651" in text_lower:
            provider = "MTN_MOMO"
        elif "orange" in text_lower or "om" in text_lower or "69" in text_lower or "655" in text_lower or "656" in text_lower:
            provider = "ORANGE_MONEY"

        # Extract all numbers from text
        all_numbers = DeterministicFinancialValidator.extract_all_numbers(sms_text)
        phones = DeterministicFinancialValidator.CAMEROON_PHONE_PATTERN.findall(sms_text)
        recipient = phones[0] if phones else None

        # Look for reference ID
        ref_match = cls.REF_PATTERN.search(sms_text)
        tx_ref = ref_match.group(1) if ref_match else "REF-AUTOGEN"

        # Heuristic identification of transfer amount, fee, and balance
        # Usually: Amount is primary, fee is smaller (e.g. 50-2500), new balance is large
        amount = 0.0
        fee = 0.0
        new_balance = None

        # Specific extraction via regex patterns
        fee_match = re.search(r'frais[:\s]+(\d+[\s,.]?\d*)\s*(?:fcfa|xaf)?', sms_text, re.IGNORECASE)
        if fee_match:
            fee = DeterministicFinancialValidator.parse_amount(fee_match.group(1)) or 0.0

        bal_match = re.search(r'(?:nouveau\s+solde|solde\s+restant|solde)[:\s]+(\d+[\s,.]?\d*)\s*(?:fcfa|xaf)?', sms_text, re.IGNORECASE)
        if bal_match:
            new_balance = DeterministicFinancialValidator.parse_amount(bal_match.group(1))

        # Amount is the primary transaction figure (often right after 'transfert de' or 'reçu')
        amt_match = re.search(r'(?:transfert\s+de|transf[eé]r[eé]|montant[:\s]+)\s*(\d+[\s,.]?\d*)', sms_text, re.IGNORECASE)
        if amt_match:
            amount = DeterministicFinancialValidator.parse_amount(amt_match.group(1)) or 0.0
        elif len(all_numbers) >= 1:
            amount = all_numbers[0]

        total_deducted = amount + fee

        # Mathematical consistency check
        is_consistent = True
        discrepancy = 0.0
        notes = []

        if previous_balance is not None and new_balance is not None:
            expected_new_balance = previous_balance - total_deducted
            diff = abs(expected_new_balance - new_balance)
            if diff > 0.01:
                is_consistent = False
                discrepancy = round(diff, 2)
                notes.append(
                    f"DISCREPANCY: Previous ({previous_balance}) - Total ({total_deducted}) = "
                    f"Expected ({expected_new_balance}), but SMS indicates ({new_balance})."
                )
            else:
                notes.append(f"VERIFIED: Previous ({previous_balance}) - Total ({total_deducted}) = New Balance ({new_balance})")
        else:
            notes.append(f"Extracted Amount: {amount} FCFA, Fee: {fee} FCFA, Total: {total_deducted} FCFA.")

        return ParsedMobileMoneySMS(
            provider=provider,
            transaction_type="TRANSFER",
            amount=amount,
            fee=fee,
            total_deducted=total_deducted,
            new_balance=new_balance,
            recipient_or_sender=recipient,
            transaction_reference=tx_ref,
            currency="FCFA",
            is_mathematically_consistent=is_consistent,
            discrepancy_amount=discrepancy,
            notes=notes
        )

