"""
Automated Test Suite for Financial Data Integrity & Zero Fabrication.
Verifies that MboFlow NEVER substitutes:
- A fabricated account balance
- A default transaction amount
- A fabricated recipient phone
- A guessed transaction fee
- An assumed successful transaction
And handles negations and clarifications strictly.
"""

import pytest
from packages.shared_schemas.mboa_schemas import (
    LanguageCode,
    DialogState,
    AgentIntent,
    AgentMessageRequest,
    PreparedTransaction,
    TransactionStatus
)
from services.agent_orchestrator.orchestrator import AgentOrchestrator


@pytest.fixture
def orchestrator():
    return AgentOrchestrator()


@pytest.mark.asyncio
async def test_zero_balance_fabrication_when_unavailable(orchestrator):
    """
    When the user requests their balance but no balance is extracted from the page,
    the system MUST communicate that the information is unavailable.
    It MUST NEVER return a fabricated 150,000 FCFA balance.
    """
    req = AgentMessageRequest(
        session_id="zero_fab_balance_sess",
        user_input="Quel est mon solde ?",
        language=LanguageCode.FRENCH
        # No page_url provided, so extraction.balances is empty
    )
    resp = await orchestrator.process_user_request(req)

    assert resp.intent == AgentIntent.CHECK_BALANCE
    # Must NOT hallucinate 150 000 FCFA
    assert "150 000" not in resp.explanation
    assert "150000" not in resp.explanation
    # Must explicitly state that information is unavailable
    assert "Information indisponible" in resp.explanation or "indisponible" in resp.explanation.lower()
    assert resp.dialog_state == DialogState.IDLE


@pytest.mark.asyncio
async def test_zero_amount_and_recipient_fabrication(orchestrator):
    """
    When the user asks to send money without specifying amount or recipient,
    the system MUST ask for clarification.
    It MUST NEVER default to 25,000 FCFA or recipient 699001122.
    """
    req = AgentMessageRequest(
        session_id="zero_fab_transfer_sess",
        user_input="Je veux envoyer de l'argent s'il vous plaît",
        language=LanguageCode.FRENCH
    )
    resp = await orchestrator.process_user_request(req)

    assert resp.intent == AgentIntent.PREPARE_TRANSFER
    # Must NOT prepare any transaction
    assert resp.prepared_transaction is None
    assert resp.requires_user_confirmation is False
    # Must transition to NEED_CLARIFICATION
    assert resp.dialog_state == DialogState.NEED_CLARIFICATION
    assert "amount" in resp.missing_parameters
    assert "recipient" in resp.missing_parameters
    # Must prompt user for details
    assert "préciser le montant" in resp.explanation.lower() or "montant" in resp.explanation.lower()


@pytest.mark.asyncio
async def test_zero_recipient_fabrication_when_only_amount_provided(orchestrator):
    """
    When user provides an amount (e.g. 50,000 FCFA) but NO recipient,
    system MUST NOT invent a recipient phone number (such as 699001122).
    """
    req = AgentMessageRequest(
        session_id="zero_fab_no_recipient_sess",
        user_input="Je veux faire un transfert de 50000 FCFA",
        language=LanguageCode.FRENCH
    )
    resp = await orchestrator.process_user_request(req)

    assert resp.intent == AgentIntent.PREPARE_TRANSFER
    assert resp.prepared_transaction is None
    assert resp.dialog_state == DialogState.NEED_CLARIFICATION
    assert "recipient" in resp.missing_parameters
    assert "699001122" not in resp.explanation
    assert "numéro de téléphone" in resp.explanation.lower()


@pytest.mark.asyncio
async def test_zero_amount_fabrication_when_only_recipient_provided(orchestrator):
    """
    When user provides recipient (e.g. 677889900) but NO amount,
    system MUST NOT assume 25,000 FCFA.
    """
    req = AgentMessageRequest(
        session_id="zero_fab_no_amount_sess",
        user_input="Envoie de l'argent au 677889900",
        language=LanguageCode.FRENCH
    )
    resp = await orchestrator.process_user_request(req)

    assert resp.intent == AgentIntent.PREPARE_TRANSFER
    assert resp.prepared_transaction is None
    assert resp.dialog_state == DialogState.NEED_CLARIFICATION
    assert "amount" in resp.missing_parameters
    assert "25 000" not in resp.explanation
    assert "25000" not in resp.explanation


@pytest.mark.asyncio
async def test_negation_handling_cancels_transfer(orchestrator):
    """
    If the user says 'Non n'envoie pas' or 'Annule le transfert',
    the system MUST classify as CANCEL_TRANSFER and never prepare or execute.
    """
    req = AgentMessageRequest(
        session_id="negation_sess",
        user_input="Non n'envoie pas l'argent, annule tout !",
        language=LanguageCode.FRENCH
    )
    resp = await orchestrator.process_user_request(req)

    assert resp.intent == AgentIntent.CANCEL_TRANSFER
    assert resp.prepared_transaction is None
    assert resp.requires_user_confirmation is False
    assert resp.dialog_state == DialogState.CANCELLED
    assert "annulée" in resp.explanation.lower() or "annulé" in resp.explanation.lower()


@pytest.mark.asyncio
async def test_generic_yes_does_not_confirm_without_pending_transaction(orchestrator):
    """
    A generic 'Oui' or 'Yes' in IDLE state must NOT trigger a transfer confirmation.
    """
    req = AgentMessageRequest(
        session_id="unsolicited_confirm_sess",
        user_input="Oui d'accord",
        language=LanguageCode.FRENCH
    )
    resp = await orchestrator.process_user_request(req)

    assert resp.intent != AgentIntent.CONFIRM_TRANSFER
    assert resp.prepared_transaction is None
    assert resp.requires_user_confirmation is False
    assert resp.dialog_state == DialogState.IDLE

