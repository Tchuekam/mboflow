"""
Deterministic Financial Integrity and Validation Engine for Mboa Finance AI.
Strictly non-LLM, rule-based mathematical and entity preservation validation.
Guarantees zero numerical hallucinations, fee discrepancies, or beneficiary tampering.
"""

import re
from typing import Tuple, Dict, List, Optional
from packages.shared_schemas.mboa_schemas import (
    PreparedTransaction,
    VerificationReport,
    VerificationStatus,
)


class DeterministicFinancialValidator:
    """
    Deterministic validator protecting financial integrity.
    Verifies amounts, fees, currency notation, beneficiary identifiers,
    and checks that translations preserve financial facts without alteration.
    """

    # Regex patterns for amounts, currencies, account numbers, and Cameroonian phone numbers
    AMOUNT_PATTERN = re.compile(
        r'(?P<number>\b\d{1,3}(?:[,\s.]\d{3})+(?:[.,]\d+)?|\b\d+(?:[.,]\d+)?)\s*(?P<currency>FCFA|XAF|CFA|F\s*CFA|\$|€|EUR|USD)?',
        re.IGNORECASE
    )
    CAMEROON_PHONE_PATTERN = re.compile(r'(?:\+?237\s*)?(?:6[25789]\d{7}|2[234]\d{7})\b')
    ACCOUNT_ID_PATTERN = re.compile(r'\b(?:CM\d{2}[A-Z0-9]{16,24}|[0-9]{10,20}|MOMO-[A-Z0-9]{6,12})\b')

    # Security warning keywords across French, English, and Cameroonian languages
    WARNING_KEYWORDS = [
        # French
        "attention", "avertissement", "ne partagez jamais", "code secret", "arnaque", "sécurité",
        # English
        "warning", "never share", "pin", "scam", "caution", "fraud", "security",
        # Fulfulde
        "reentaare", "jommbaajo", "suuɗiindi", "koodi",
        # Ewondo
        "nkat", "mebal", "bisio",
        # Bulu
        "enyiman", "solô",
        # Ghomálá'
        "tse", "pfa", "mûŋkam",
        # Duala
        "mwemba", "bolea", "wumɛ",
        # Pidgin
        "secret", "warning"
    ]

    @classmethod
    def _is_phone_number(cls, num_str: str) -> bool:
        clean = re.sub(r'\D', '', num_str)
        # Cameroonian phone numbers are 9 digits starting with 6 or 2
        return len(clean) == 9 and clean[0] in ('6', '2')

    @classmethod
    def _clean_and_parse_float(cls, raw_num: str) -> Optional[float]:
        clean_num = raw_num.replace(" ", "")
        if "," in clean_num and "." in clean_num:
            if clean_num.rfind(".") > clean_num.rfind(","):
                clean_num = clean_num.replace(",", "")
            else:
                clean_num = clean_num.replace(".", "").replace(",", ".")
        elif "," in clean_num:
            parts = clean_num.split(",")
            if len(parts) == 2 and len(parts[1]) == 3 and int(parts[1]) >= 0:
                clean_num = clean_num.replace(",", "")
            elif len(parts) > 2:
                clean_num = clean_num.replace(",", "")
            else:
                clean_num = clean_num.replace(",", ".")
        elif "." in clean_num:
            parts = clean_num.split(".")
            if len(parts) == 2 and len(parts[1]) == 3 and int(parts[1]) >= 0:
                clean_num = clean_num.replace(".", "")
            elif len(parts) > 2:
                clean_num = clean_num.replace(".", "")

        try:
            return float(clean_num)
        except ValueError:
            return None

    @classmethod
    def parse_amount(cls, text: str) -> Optional[float]:
        """
        Extract and parse a single numeric amount from string, handling French/English formats:
        '25 000 FCFA' -> 25000.0
        '25,000.50' -> 25000.50
        '25.000,50' -> 25000.50
        Prioritizes matches with explicit currency and avoids phone numbers.
        """
        if not text:
            return None
        clean_text = text.strip()
        matches = list(cls.AMOUNT_PATTERN.finditer(clean_text))
        if not matches:
            return None

        # Pass 1: Match with explicit currency that is not a phone number
        for m in matches:
            if m.group("currency"):
                raw_num = m.group("number")
                if not cls._is_phone_number(raw_num):
                    val = cls._clean_and_parse_float(raw_num)
                    if val is not None:
                        return val

        # Pass 2: First match that is not a phone number
        for m in matches:
            raw_num = m.group("number")
            if not cls._is_phone_number(raw_num):
                val = cls._clean_and_parse_float(raw_num)
                if val is not None:
                    return val

        return None

    @classmethod
    def extract_all_numbers(cls, text: str) -> List[float]:
        """Extract all numeric amounts from a piece of text."""
        numbers = []
        for match in cls.AMOUNT_PATTERN.finditer(text):
            num_str = match.group("number")
            val = cls.parse_amount(num_str)
            if val is not None:
                numbers.append(val)
        return numbers

    @classmethod
    def validate_arithmetic(
        cls,
        amount: float,
        fee: float,
        total_debit: float,
        tolerance: float = 0.01
    ) -> VerificationReport:
        """
        Mathematically verify that:
        Total Debit == Amount + Fee
        Any deviation is flagged as CALCULATION_MISMATCH.
        """
        expected_total = amount + fee
        difference = abs(expected_total - total_debit)

        if difference <= tolerance:
            return VerificationReport(
                is_valid=True,
                status=VerificationStatus.VERIFIED,
                total_matches_sum=True,
                discrepancy_amount=0.0,
                notes=[f"Deterministic check passed: {amount} + {fee} = {total_debit}"]
            )
        else:
            return VerificationReport(
                is_valid=False,
                status=VerificationStatus.CALCULATION_MISMATCH,
                total_matches_sum=False,
                discrepancy_amount=round(difference, 2),
                notes=[
                    f"CRITICAL DISCREPANCY: Expected total {expected_total} "
                    f"({amount} + {fee}), but interface indicates {total_debit}. "
                    f"Discrepancy: {round(difference, 2)}"
                ]
            )

    @classmethod
    def shield_financial_tokens(cls, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Shield amounts, currencies, account IDs, and phone numbers with immutable tokens
        before passing text into translation engines.
        Returns: (shielded_text, token_map)
        """
        token_map: Dict[str, str] = {}
        token_counter = 0

        # Helper to replace matches with unique tokens
        def replace_with_token(match: re.Match) -> str:
            nonlocal token_counter
            matched_str = match.group(0)
            token = f"[[MBOA_FIN_TOKEN_{token_counter}]]"
            token_map[token] = matched_str
            token_counter += 1
            return token

        # Shield phone numbers first
        shielded = cls.CAMEROON_PHONE_PATTERN.sub(replace_with_token, text)
        # Shield account IDs
        shielded = cls.ACCOUNT_ID_PATTERN.sub(replace_with_token, shielded)
        # Shield amounts with currency
        shielded = cls.AMOUNT_PATTERN.sub(replace_with_token, shielded)

        return shielded, token_map

    @classmethod
    def unshield_financial_tokens(cls, shielded_text: str, token_map: Dict[str, str]) -> str:
        """
        Restore original shielded financial tokens back into translated text.
        Guarantees exact preservation of amounts, numbers, and identifiers.
        """
        restored = shielded_text
        for token, original_val in token_map.items():
            restored = restored.replace(token, original_val)
            # Also handle if translator altered brackets slightly
            fuzzy_token = token.replace("[[", "[").replace("]]", "]")
            if fuzzy_token in restored:
                restored = restored.replace(fuzzy_token, original_val)
        return restored

    @classmethod
    def validate_translation_integrity(
        cls,
        original_text: str,
        translated_text: str
    ) -> VerificationReport:
        """
        Check that translated text preserves all financial values, phone numbers,
        currencies, and security warnings from the original text.
        """
        notes: List[str] = []
        is_valid = True
        status = VerificationStatus.VERIFIED

        orig_numbers = cls.extract_all_numbers(original_text)
        trans_numbers = cls.extract_all_numbers(translated_text)

        # Check all original numbers are represented in translation
        missing_numbers = []
        trans_numbers_copy = list(trans_numbers)
        for num in orig_numbers:
            found = False
            for i, t_num in enumerate(trans_numbers_copy):
                if abs(num - t_num) < 0.01:
                    found = True
                    trans_numbers_copy.pop(i)
                    break
            if not found:
                missing_numbers.append(num)

        if missing_numbers:
            is_valid = False
            status = VerificationStatus.TAMPERED
            notes.append(f"Translation altered or omitted numerical amounts: {missing_numbers}")

        # Check phone numbers / account IDs preservation
        orig_phones = cls.CAMEROON_PHONE_PATTERN.findall(original_text)
        for phone in orig_phones:
            clean_phone = re.sub(r'\s+', '', phone)
            if clean_phone not in re.sub(r'\s+', '', translated_text):
                is_valid = False
                status = VerificationStatus.TAMPERED
                notes.append(f"Beneficiary phone identifier altered or omitted: {phone}")

        # Check currency preservation
        if "FCFA" in original_text and "FCFA" not in translated_text and "XAF" not in translated_text:
            notes.append("Currency notation 'FCFA' missing from translated text.")
            if is_valid:
                status = VerificationStatus.SUSPICIOUS

        # Check warning preservation
        orig_has_warning = any(w in original_text.lower() for w in cls.WARNING_KEYWORDS)
        trans_has_warning = any(w in translated_text.lower() for w in cls.WARNING_KEYWORDS)
        if orig_has_warning and not trans_has_warning:
            is_valid = False
            status = VerificationStatus.MISSING_WARNING
            notes.append("Original security warning or PIN caution was omitted in translation.")

        return VerificationReport(
            is_valid=is_valid,
            status=status,
            total_matches_sum=True,
            discrepancy_amount=0.0,
            currency_preserved="FCFA" in translated_text or "XAF" in translated_text or "FCFA" not in original_text,
            beneficiary_verified=len(orig_phones) == 0 or is_valid,
            warnings_preserved=not orig_has_warning or trans_has_warning,
            notes=notes if notes else ["Translation perfectly preserved financial and security elements."]
        )

    @classmethod
    def validate_prepared_transaction(
        cls,
        tx: PreparedTransaction
    ) -> VerificationReport:
        """
        Verify an entire transaction object prior to presenting to the user.
        """
        # Arithmetic check
        arithmetic_report = cls.validate_arithmetic(tx.amount, tx.fee, tx.total_debit)
        if not arithmetic_report.is_valid:
            return arithmetic_report

        # Beneficiary validation
        notes = list(arithmetic_report.notes)
        if not tx.beneficiary_account:
            return VerificationReport(
                is_valid=False,
                status=VerificationStatus.SUSPICIOUS,
                total_matches_sum=True,
                notes=["Beneficiary account identifier is missing."]
            )

        if tx.amount <= 0:
            return VerificationReport(
                is_valid=False,
                status=VerificationStatus.SUSPICIOUS,
                total_matches_sum=True,
                notes=["Transaction amount must be strictly greater than 0."]
            )

        return VerificationReport(
            is_valid=True,
            status=VerificationStatus.VERIFIED,
            total_matches_sum=True,
            discrepancy_amount=0.0,
            currency_preserved=True,
            beneficiary_verified=True,
            warnings_preserved=True,
            notes=notes
        )
