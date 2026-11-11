"""
Comprehensive Automated Test Suite for Mboa Finance AI.
Validates Mandatory Scenarios A through G:
- Scenario A: Voice interaction (French)
- Scenario B: National language interaction (Fulfulde, Ewondo, Bulu, Ghomálá', Duala, Pidgin)
- Scenario C: Full interface translation
- Scenario D: Deterministic financial accuracy (150,000 / 25,000 / 250 / 25,250 FCFA)
- Scenario E: Dynamic content detection and translation
- Scenario F: Prepared transaction and explicit confirmation workflow
- Scenario G: Error recovery and boundary conditions
"""

import pytest
import time
import os
from packages.shared_schemas.mboa_schemas import (
    LanguageCode,
    VerificationStatus,
    TransactionStatus,
    AgentIntent,
    AgentMessageRequest,
    PreparedTransaction,
    SynthesisRequest
)
from packages.language_registry.registry import LanguageRegistry
from packages.financial_validation.validator import DeterministicFinancialValidator
from packages.security.action_guard import ActionGuard, SecurityViolationError
from services.translation.engine import ContextAwareTranslationEngine
from services.speech_to_text.engine import SpeechToTextEngine
from services.text_to_speech.engine import TextToSpeechEngine
from services.interface_extraction.extractor import InterfaceExtractor
from services.agent_orchestrator.orchestrator import AgentOrchestrator


@pytest.fixture
def sim_html():
    path = os.path.join(os.path.dirname(__file__), "..", "simulated-bank", "index.html")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def translation_engine():
    return ContextAwareTranslationEngine()


@pytest.fixture
def financial_validator():
    return DeterministicFinancialValidator()


@pytest.fixture
def extractor():
    return InterfaceExtractor()


@pytest.fixture
def action_guard():
    return ActionGuard()


@pytest.fixture
def orchestrator():
    return AgentOrchestrator()


# ----------------------------------------------------------------------
# SCENARIO A: Voice Interaction (French)
# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_scenario_a_voice_interaction_french(orchestrator):
    """
    User speaks in French: 'Montre-moi mon solde'
    System understands intent, formats balance response, and generates TTS audio.
    """
    request = AgentMessageRequest(
        session_id="test_session_fr",
        user_input="Montre-moi mon solde",
        language=LanguageCode.FRENCH
    )
    response = await orchestrator.process_user_request(request)

    assert response.detected_language == LanguageCode.FRENCH
    assert response.intent == AgentIntent.CHECK_BALANCE
    assert "150 000 FCFA" in response.explanation or "150000" in response.explanation
    assert response.audio_base64 is not None  # TTS waveform generated
    assert len(response.steps) >= 3


# ----------------------------------------------------------------------
# SCENARIO B: National Language Interaction
# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_scenario_b_national_languages(orchestrator, translation_engine):
    """
    Test interaction across Cameroonian languages:
    Fulfulde, Ewondo, Bulu, Ghomálá', Duala, and Pidgin English.
    """
    test_cases = [
        (LanguageCode.FULFULDE, "Holle yam ceede am", "Ceede"),
        (LanguageCode.EWONDO, "Lere ma moni wom", "Moni"),
        (LanguageCode.BULU, "Lere ma moni wom", "Moni"),
        (LanguageCode.GHOMALA, "Zǎk ma nkáp yəm", "Nkáp"),
        (LanguageCode.DUALA, "Bolo mba moto mwam", "Moto"),
        (LanguageCode.PIDGIN, "Show me ma balance", "balance")
    ]

    for lang, input_phrase, expected_keyword in test_cases:
        # Check language registry capability
        cap = LanguageRegistry.get_language(lang.value)
        assert cap is not None
        assert cap.speech_input_supported is True
        assert cap.translation_supported is True

        # Process message
        req = AgentMessageRequest(
            session_id=f"session_{lang.value}",
            user_input=input_phrase,
            language=lang
        )
        resp = await orchestrator.process_user_request(req)

        assert resp.detected_language == lang
        assert resp.intent == AgentIntent.CHECK_BALANCE
        # Explanation must contain the verified numeric amount 150 000 FCFA
        assert "150 000" in resp.explanation or "150000" in resp.explanation
        # Explanation must contain appropriate vernacular terminology
        assert expected_keyword.lower() in resp.explanation.lower()


# ----------------------------------------------------------------------
# SCENARIO C: Full Interface Translation
# ----------------------------------------------------------------------
def test_scenario_c_full_interface_translation(sim_html, extractor, translation_engine):
    """
    System parses simulated French financial interface and translates its content into Fulfulde.
    Verifies that layout nodes are extracted and translated accurately.
    """
    extraction = extractor.extract_from_html(sim_html, page_url="http://localhost:8000/bank")

    assert len(extraction.elements) > 10
    assert len(extraction.balances) >= 1
    assert len(extraction.fees) >= 1

    # Translate extracted text nodes to Fulfulde
    translated_count = 0
    for el in extraction.elements[:15]:
        if el.original_text.strip():
            translated, report = translation_engine.translate(
                el.original_text,
                source_lang=LanguageCode.FRENCH,
                target_lang=LanguageCode.FULFULDE
            )
            assert report.is_valid is True
            translated_count += 1

    assert translated_count > 0


# ----------------------------------------------------------------------
# SCENARIO D: Financial Accuracy (Strict Deterministic Validation)
# ----------------------------------------------------------------------
def test_scenario_d_financial_accuracy(sim_html, extractor, financial_validator, translation_engine):
    """
    Target values:
    - Balance: 150,000 FCFA
    - Transfer amount: 25,000 FCFA
    - Fee: 250 FCFA
    - Total debit: 25,250 FCFA
    Must strictly satisfy Total = Amount + Fee and retain exact numbers in translation.
    """
    extraction = extractor.extract_from_html(sim_html)

    # 1. Check extracted amounts
    all_raw_text = extraction.raw_text
    numbers = financial_validator.extract_all_numbers(all_raw_text)

    assert 150000.0 in numbers
    assert 25000.0 in numbers
    assert 250.0 in numbers
    assert 25250.0 in numbers

    # 2. Deterministic mathematical check
    report = financial_validator.validate_arithmetic(
        amount=25000.0,
        fee=250.0,
        total_debit=25250.0
    )
    assert report.is_valid is True
    assert report.status == VerificationStatus.VERIFIED
    assert report.total_matches_sum is True
    assert report.discrepancy_amount == 0.0

    # 3. Check calculation mismatch detection (Simulate fee discrepancy)
    invalid_report = financial_validator.validate_arithmetic(
        amount=25000.0,
        fee=250.0,
        total_debit=26000.0  # Incorrect total debit!
    )
    assert invalid_report.is_valid is False
    assert invalid_report.status == VerificationStatus.CALCULATION_MISMATCH
    assert invalid_report.discrepancy_amount == 750.0

    # 4. Check Translation Integrity Protection
    original_sentence = (
        "Montant du transfert: 25 000 FCFA. "
        "Frais de transfert: 250 FCFA. "
        "Total débité: 25 250 FCFA."
    )
    translated_sentence, trans_report = translation_engine.translate(
        original_sentence,
        source_lang=LanguageCode.FRENCH,
        target_lang=LanguageCode.FULFULDE
    )

    assert trans_report.is_valid is True
    assert trans_report.status == VerificationStatus.VERIFIED
    # Numbers must be strictly preserved
    assert "25 000" in translated_sentence
    assert "250" in translated_sentence
    assert "25 250" in translated_sentence
    assert "FCFA" in translated_sentence


# ----------------------------------------------------------------------
# SCENARIO E: Dynamic Content Ingestion
# ----------------------------------------------------------------------
def test_scenario_e_dynamic_content_detection(extractor, translation_engine):
    """
    Simulate a newly introduced financial message arriving after initial page render:
    'Alerte de sécurité: Maintenance planifiée des services de 02h00 à 04h00. Aucun frais supplémentaire.'
    System must extract and translate it immediately.
    """
    dynamic_html_snippet = """
    <div id="dynamic-alert-123" class="dynamic-banner" data-dynamic="true">
        Avertissement de sécurité: Maintenance planifiée des serveurs de 02h00 à 04h00.
    </div>
    """
    extraction = extractor.extract_from_html(dynamic_html_snippet)
    assert len(extraction.elements) >= 1
    dynamic_el = extraction.elements[0]
    assert dynamic_el.is_dynamic is True

    # Translate dynamically introduced message
    translated, report = translation_engine.translate(
        dynamic_el.original_text,
        source_lang=LanguageCode.FRENCH,
        target_lang=LanguageCode.EWONDO
    )
    assert report.is_valid is True
    assert "02h00" in translated or "2" in translated
    assert report.warnings_preserved is True


# ----------------------------------------------------------------------
# SCENARIO F: Prepared Transaction & Explicit User Confirmation
# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_scenario_f_prepared_transaction_workflow(orchestrator, action_guard):
    """
    User requests transfer of 25,000 FCFA to 699001122.
    Agent prepares transaction, computes fees, verifies math, but DOES NOT execute.
    Transaction requires explicit confirmation.
    """
    # Phase 1: Prepare
    req = AgentMessageRequest(
        session_id="tx_session_1",
        user_input="Je veux envoyer 25000 FCFA au numéro 699001122",
        language=LanguageCode.FRENCH
    )
    resp = await orchestrator.process_user_request(req)

    assert resp.intent == AgentIntent.PREPARE_TRANSFER
    assert resp.requires_user_confirmation is True
    assert resp.prepared_transaction is not None
    tx = resp.prepared_transaction
    assert tx.amount == 25000.0
    assert tx.fee == 250.0
    assert tx.total_debit == 25250.0
    assert tx.status == TransactionStatus.PENDING_CONFIRMATION
    assert tx.verification_status == VerificationStatus.VERIFIED

    # Phase 2: Confirm
    confirm_req = AgentMessageRequest(
        session_id="tx_session_1",
        user_input="Oui je confirme le transfert",
        language=LanguageCode.FRENCH
    )
    confirm_resp = await orchestrator.process_user_request(confirm_req)

    assert confirm_resp.intent == AgentIntent.CONFIRM_TRANSFER
    assert confirm_resp.prepared_transaction is not None
    assert confirm_resp.prepared_transaction.status == TransactionStatus.CONFIRMED
    assert confirm_resp.prepared_transaction.confirmed_at is not None

    # Check audit trail
    audit_events = orchestrator.action_guard.get_audit_trail()
    assert len(audit_events) >= 2
    assert audit_events[-1]["event_type"] == "TRANSACTION_CONFIRMED_SIMULATED"


# ----------------------------------------------------------------------
# SCENARIO G: Error Recovery and Boundary Conditions
# ----------------------------------------------------------------------
def test_scenario_g_recovery_tampered_translation(translation_engine, financial_validator):
    """
    Simulate an unauthorized alteration of financial amounts:
    Original has 25,000 FCFA, but tampered translation modifies it to 35,000 FCFA.
    Validator must flag it as TAMPERED and refuse verification.
    """
    original = "Montant du transfert: 25 000 FCFA"
    tampered_translation = "Neldol ceede: 35 000 FCFA"  # Modified amount!

    report = financial_validator.validate_translation_integrity(original, tampered_translation)
    assert report.is_valid is False
    assert report.status == VerificationStatus.TAMPERED
    assert "altered or omitted" in report.notes[0]


def test_scenario_g_recovery_omitted_warning(financial_validator):
    """
    Original contains critical PIN security warning, but translation drops it.
    Validator must flag MISSING_WARNING.
    """
    original = "Attention: Ne partagez jamais votre code secret PIN."
    tampered = "Moni mese ma vɔ̂k."  # Warning completely omitted

    report = financial_validator.validate_translation_integrity(original, tampered)
    assert report.is_valid is False
    assert report.status == VerificationStatus.MISSING_WARNING


def test_scenario_g_recovery_action_guard_violation(action_guard):
    """
    Attempting to confirm a transaction that does not exist or has already been completed.
    Must raise SecurityViolationError.
    """
    with pytest.raises(SecurityViolationError):
        action_guard.confirm_transaction("NON_EXISTENT_ID", explicit_user_consent=True)

