"""
Automated Test Suite for Translation Quality & Native-Speaker Benchmarks.
Verifies that:
- Numbers, amounts, phone numbers, and currencies are strictly preserved (Token Shielding).
- Security warnings and PIN caution alerts are preserved without dilution.
- Multilingual translation handles French, English, Cameroonian Pidgin, and National Languages.
- Quality benchmark evaluation mechanism verifies native-speaker reviewed samples.
"""

import pytest
from packages.shared_schemas.mboa_schemas import LanguageCode, VerificationStatus
from services.translation.engine import ContextAwareTranslationEngine, FinancialTerminologyRegistry


@pytest.fixture
def engine():
    return ContextAwareTranslationEngine()


def test_language_detection(engine):
    """Verify language detection correctly identifies French, English, and Cameroonian vernacular."""
    lang_fr, conf_fr = engine.detect_language("Bonjour, quel est le montant de mon solde disponible ?")
    assert lang_fr == LanguageCode.FRENCH
    assert conf_fr > 0.70

    lang_en, conf_en = engine.detect_language("Hello, what is my current account balance and fees?")
    assert lang_en == LanguageCode.ENGLISH
    assert conf_en > 0.70

    # Fulfulde vernacular phrase
    lang_fuv, conf_fuv = engine.detect_language("Holle yam ceede am")
    assert lang_fuv == LanguageCode.FULFULDE

    # Pidgin vernacular phrase
    lang_pcm, conf_pcm = engine.detect_language("Show me di money wey dey for my account")
    assert lang_pcm == LanguageCode.PIDGIN


def test_translation_token_shielding_preservation(engine):
    """Verify that multiple amounts, currencies, and phone numbers are untouched across translation."""
    complex_text = (
        "Transfert de 75 000 FCFA vers le numéro 699112233 avec des frais de 500 FCFA. "
        "Total débité: 75 500 FCFA."
    )
    trans, report = engine.translate(
        complex_text,
        source_lang=LanguageCode.FRENCH,
        target_lang=LanguageCode.ENGLISH
    )

    assert report.is_valid is True
    assert report.status == VerificationStatus.VERIFIED
    # Check amounts and phone numbers
    assert "75 000" in trans or "75000" in trans
    assert "699112233" in trans
    assert "500" in trans
    assert "75 500" in trans or "75500" in trans


def test_translation_preserves_critical_pin_security_warning(engine):
    """Verify that security warnings and PIN caution notices are retained."""
    warning_text = "Avertissement de sécurité: Ne partagez jamais votre code secret PIN avec qui que ce soit."
    trans, report = engine.translate(
        warning_text,
        source_lang=LanguageCode.FRENCH,
        target_lang=LanguageCode.PIDGIN
    )

    assert report.is_valid is True
    assert report.warnings_preserved is True
    assert "pin" in trans.lower()
    assert "secret" in trans.lower() or "warning" in trans.lower()


def test_native_speaker_benchmark_evaluation(engine):
    """
    Runs the native-speaker reviewed benchmark test harness
    verifying translation quality across all targeted languages.
    """
    benchmarks = [
        {
            "source_text": "Votre solde disponible est de 150 000 FCFA.",
            "source_lang": LanguageCode.FRENCH,
            "target_lang": LanguageCode.ENGLISH,
            "expected_keywords": ["balance", "FCFA"],
            "expected_amounts": [150000.0]
        },
        {
            "source_text": "Votre solde disponible est de 150 000 FCFA.",
            "source_lang": LanguageCode.FRENCH,
            "target_lang": LanguageCode.FULFULDE,
            "expected_keywords": ["Ceede", "FCFA"],
            "expected_amounts": [150000.0]
        },
        {
            "source_text": "Votre solde disponible est de 150 000 FCFA.",
            "source_lang": LanguageCode.FRENCH,
            "target_lang": LanguageCode.EWONDO,
            "expected_keywords": ["Moni", "FCFA"],
            "expected_amounts": [150000.0]
        },
        {
            "source_text": "Votre solde disponible est de 150 000 FCFA.",
            "source_lang": LanguageCode.FRENCH,
            "target_lang": LanguageCode.BULU,
            "expected_keywords": ["Moni", "FCFA"],
            "expected_amounts": [150000.0]
        },
        {
            "source_text": "Votre solde disponible est de 150 000 FCFA.",
            "source_lang": LanguageCode.FRENCH,
            "target_lang": LanguageCode.GHOMALA,
            "expected_keywords": ["Nkáp", "FCFA"],
            "expected_amounts": [150000.0]
        },
        {
            "source_text": "Votre solde disponible est de 150 000 FCFA.",
            "source_lang": LanguageCode.FRENCH,
            "target_lang": LanguageCode.DUALA,
            "expected_keywords": ["Moto", "FCFA"],
            "expected_amounts": [150000.0]
        },
        {
            "source_text": "Votre solde disponible est de 150 000 FCFA.",
            "source_lang": LanguageCode.FRENCH,
            "target_lang": LanguageCode.PIDGIN,
            "expected_keywords": ["balance", "FCFA"],
            "expected_amounts": [150000.0]
        }
    ]

    results = engine.evaluate_translation_quality(benchmarks)

    assert results["total_samples"] == len(benchmarks)
    assert results["accuracy_score_percent"] >= 95.0
    assert results["passed_samples"] == len(benchmarks)

