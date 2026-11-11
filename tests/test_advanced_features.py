"""
Automated Test Suite for Advanced Features:
- OCR Fallback Engine (Canvas & Receipt Image extraction)
- Mobile Money SMS Deterministic Validation (MTN MoMo & Orange Money)
- Cameroonian Microfinance & Tontine ("Njangi") Terminology Grounding
"""

import io
import pytest
from PIL import Image, ImageDraw
from packages.shared_schemas.mboa_schemas import LanguageCode
from services.ocr.engine import OCRFallbackEngine
from packages.financial_validation.sms_parser import MobileMoneySMSParser
from services.translation.engine import ContextAwareTranslationEngine


def create_synthetic_receipt_image(balance_str: str = "Solde: 150 000 FCFA") -> bytes:
    """Creates a synthetic black & white banking receipt image in memory."""
    img = Image.new("RGB", (400, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((20, 30), "MboaPay Microfinance", fill=(0, 0, 0))
    draw.text((20, 70), balance_str, fill=(0, 0, 0))
    draw.text((20, 110), "Frais: 250 FCFA", fill=(0, 0, 0))
    draw.text((20, 150), "Recipient: 699001122", fill=(0, 0, 0))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_ocr_fallback_processing():
    """Verify OCR fallback engine processes receipt image and extracts numbers."""
    ocr_engine = OCRFallbackEngine()
    img_bytes = create_synthetic_receipt_image()

    result = ocr_engine.extract_from_image_bytes(
        img_bytes,
        known_text_hints=[
            "Solde: 150 000 FCFA",
            "Frais: 250 FCFA",
            "Recipient: 699001122"
        ]
    )

    assert result["image_dimensions"]["width"] == 400
    assert result["image_dimensions"]["height"] == 200
    assert 150000.0 in result["all_numbers"]
    assert 250.0 in result["all_numbers"]
    assert "699001122" in result["phone_identifiers"]
    assert len(result["balances"]) >= 1
    assert len(result["fees"]) >= 1


def test_mobile_money_sms_deterministic_validation_consistent():
    """Verify SMS parser extracts amounts and confirms arithmetic consistency."""
    # Scenario: Previous balance was 150,000 FCFA. Transfer 25,000 + 250 fee leaves 124,750 FCFA.
    sms_text = (
        "MTN MoMo: Transfert de 25 000 FCFA au 699001122 effectue avec succes. "
        "Frais: 250 FCFA. Nouveau solde: 124 750 FCFA. TxID: MOMO-987654321."
    )

    parsed = MobileMoneySMSParser.parse_sms(sms_text, previous_balance=150000.0)

    assert parsed.provider == "MTN_MOMO"
    assert parsed.amount == 25000.0
    assert parsed.fee == 250.0
    assert parsed.total_deducted == 25250.0
    assert parsed.new_balance == 124750.0
    assert parsed.recipient_or_sender == "699001122"
    assert parsed.is_mathematically_consistent is True
    assert parsed.discrepancy_amount == 0.0


def test_mobile_money_sms_deterministic_validation_discrepancy():
    """Verify SMS parser detects mathematical discrepancy if bank or SMS tampered."""
    # Tampered SMS: Claims fee was 250, but subtracted 1,000 extra from balance!
    tampered_sms = (
        "Orange Money: Vous avez transfere 25000 FCFA a 699001122. "
        "Frais: 250 FCFA. Solde restant: 123 750 FCFA. Ref: MP261110.555."
    )

    parsed = MobileMoneySMSParser.parse_sms(tampered_sms, previous_balance=150000.0)

    assert parsed.provider == "ORANGE_MONEY"
    assert parsed.amount == 25000.0
    assert parsed.fee == 250.0
    # Expected was 124,750 but SMS claims 123,750 -> 1000 FCFA discrepancy!
    assert parsed.is_mathematically_consistent is False
    assert parsed.discrepancy_amount == 1000.0
    assert "DISCREPANCY" in parsed.notes[0]


def test_tontine_and_microfinance_terminology():
    """Verify authentic Cameroonian tontine and microfinance terms translate accurately."""
    trans_engine = ContextAwareTranslationEngine()

    # Test Tontine -> Fulfulde (Kawtal ceede)
    trans_fuv, report_fuv = trans_engine.translate("Tontine", LanguageCode.FRENCH, LanguageCode.FULFULDE)
    assert report_fuv.is_valid is True
    assert "Kawtal ceede" in trans_fuv

    # Test Tontine -> Ewondo (Nkuñ)
    trans_ewo, report_ewo = trans_engine.translate("Tontine", LanguageCode.FRENCH, LanguageCode.EWONDO)
    assert report_ewo.is_valid is True
    assert "Nkuñ" in trans_ewo

@pytest.mark.asyncio
async def test_api_sms_parser_endpoint():
    """Verify REST API /api/v1/financial/parse-sms endpoint."""
    import httpx
    from apps.backend.main import app

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/financial/parse-sms",
            json={
                "sms_text": "MTN MoMo: Transfert de 25000 FCFA au 699001122. Frais: 250 FCFA. Nouveau solde: 124750 FCFA. TxID: 123.",
                "previous_balance": 150000.0
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["amount"] == 25000.0
        assert data["fee"] == 250.0
        assert data["is_mathematically_consistent"] is True

