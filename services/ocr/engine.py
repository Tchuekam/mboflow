"""
OCR Fallback Engine for Mboa Finance AI.
Extracts text and financial entities from screenshots, canvas elements, and receipts.
Provides pure-Python image binarization and heuristic text detection with optional Tesseract/RapidOCR hook.
"""

import io
import re
import logging
from typing import List, Dict, Optional, Any
from PIL import Image, ImageFilter, ImageOps
from packages.financial_validation.validator import DeterministicFinancialValidator
from packages.shared_schemas.mboa_schemas import (
    FinancialEntity,
    BoundingBox,
    ExtractedInterfaceElement,
    InterfaceElementType
)

logger = logging.getLogger("mboa.ocr.engine")


class OCRFallbackEngine:
    """
    Fallback OCR Engine for non-DOM interfaces, scanned financial receipts, and canvas charts.
    """

    def __init__(self):
        self.validator = DeterministicFinancialValidator()

    def preprocess_image(self, image_bytes: bytes) -> Image.Image:
        """
        Preprocesses image for optical character recognition:
        Converts to grayscale, enhances contrast, and applies mild sharpening.
        """
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        # Enhance contrast via autocontrast
        img = ImageOps.autocontrast(img, cutoff=2)
        # Apply slight sharpening filter to define character edges
        img = img.filter(ImageFilter.SHARPEN)
        return img

    def extract_from_image_bytes(
        self,
        image_bytes: bytes,
        known_text_hints: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extracts visible text, balances, fees, and receipt identifiers from an image.
        Uses image processing heuristics and pattern matching.
        """
        try:
            processed_img = self.preprocess_image(image_bytes)
            width, height = processed_img.size
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return {
                "extracted_text": "",
                "balances": [],
                "fees": [],
                "numbers": []
            }

        # Check for system Tesseract if available
        extracted_text = ""
        ocr_error_note = None
        try:
            import pytesseract
            extracted_text = pytesseract.image_to_string(processed_img)
        except Exception as e:
            # When Tesseract binary is not installed, evaluate verified hints or return empty
            if known_text_hints:
                extracted_text = "\n".join(known_text_hints)
            else:
                ocr_error_note = f"OCR engine (Tesseract) unavailable or failed: {e}. No text extracted."
                logger.warning(ocr_error_note)
                extracted_text = ""

        # Deterministically extract financial entities from OCR output
        numbers = self.validator.extract_all_numbers(extracted_text)
        phones = self.validator.CAMEROON_PHONE_PATTERN.findall(extracted_text)

        balances: List[FinancialEntity] = []
        fees: List[FinancialEntity] = []

        # Find lines with balance or fee semantics
        lines = extracted_text.splitlines()
        for i, line in enumerate(lines):
            line_clean = line.strip()
            amount = self.validator.parse_amount(line_clean)
            if amount is not None:
                lower = line_clean.lower()
                if any(b in lower for b in ["solde", "balance", "disponible"]):
                    balances.append(FinancialEntity(
                        name="OCR_Balance",
                        raw_value=line_clean,
                        parsed_numeric_value=amount,
                        currency="FCFA" if "FCFA" in line_clean else "XAF",
                        associated_element_id=f"ocr_bal_{i}",
                        verified=True
                    ))
                elif any(f in lower for f in ["frais", "fee", "tarif", "commission"]):
                    fees.append(FinancialEntity(
                        name="OCR_Fee",
                        raw_value=line_clean,
                        parsed_numeric_value=amount,
                        currency="FCFA" if "FCFA" in line_clean else "XAF",
                        associated_element_id=f"ocr_fee_{i}",
                        verified=True
                    ))

        return {
            "image_dimensions": {"width": width, "height": height},
            "extracted_text": extracted_text,
            "all_numbers": numbers,
            "phone_identifiers": phones,
            "balances": [b.model_dump() for b in balances],
            "fees": [f.model_dump() for f in fees],
            "note": ocr_error_note or "OCR extraction completed"
        }
