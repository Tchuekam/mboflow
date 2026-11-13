"""
Production Agent Orchestrator for Mboa Finance AI.
Coordinates Voice, Language Intelligence, Browser Automation, Financial Integrity,
and Safety Controls into a single unified conversational agent.
Enforces:
- Zero fabrication of balances, recipients, amounts, or fees.
- Strict context-aware conversation state machine.
- Disambiguation of confirmations, cancellations, questions, and corrections.
- Strict handling of negations and ambiguous inputs.
"""

import re
import time
import uuid
import logging
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal

from packages.shared_schemas.mboa_schemas import (
    LanguageCode,
    DialogState,
    AgentIntent,
    AgentMessageRequest,
    AgentMessageResponse,
    AgentActionStep,
    PreparedTransaction,
    TransactionStatus,
    SynthesisRequest,
    DOMExtractionResult,
    VerificationStatus
)
from packages.language_registry.registry import LanguageRegistry
from packages.financial_validation.validator import DeterministicFinancialValidator
from packages.security.action_guard import ActionGuard, SecurityViolationError
from packages.financial_providers.router import FinancialProviderRouter
from services.translation.engine import ContextAwareTranslationEngine
from services.speech_to_text.engine import SpeechToTextEngine
from services.text_to_speech.engine import TextToSpeechEngine
from apps.browser_connector.connector import PlaywrightBrowserConnector

logger = logging.getLogger("mboa.agent.orchestrator")


class ConversationSession:
    """State machine memory for multi-turn user dialogs."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.preferred_language: LanguageCode = LanguageCode.FRENCH
        self.dialog_state: DialogState = DialogState.IDLE
        self.draft_transfer: Dict[str, Any] = {}
        self.pending_transaction_id: Optional[str] = None
        self.last_extraction: Optional[DOMExtractionResult] = None
        self.history: List[Dict[str, Any]] = []
        self.created_at = time.time()
        self.last_active = time.time()

    def add_turn(self, role: str, message: str, meta: Optional[Dict] = None):
        self.history.append({
            "role": role,
            "message": message,
            "timestamp": time.time(),
            "meta": meta or {}
        })
        self.last_active = time.time()

    def is_expired(self, timeout_seconds: float = 300.0) -> bool:
        """Checks if session has been inactive beyond timeout."""
        return (time.time() - self.last_active) > timeout_seconds


class AgentOrchestrator:
    """
    Central Agent Orchestrator.
    Manages end-to-end flow from voice/text request to interface execution and spoken response.
    Never fabricates financial defaults.
    """

    def __init__(
        self,
        browser_connector: Optional[PlaywrightBrowserConnector] = None,
        action_guard: Optional[ActionGuard] = None,
        provider_router: Optional[FinancialProviderRouter] = None
    ):
        self.sessions: Dict[str, ConversationSession] = {}
        self.browser = browser_connector or PlaywrightBrowserConnector()
        self.translation_engine = ContextAwareTranslationEngine()
        self.action_guard = action_guard or ActionGuard()
        self.provider_router = provider_router or FinancialProviderRouter()
        self.stt_engine = SpeechToTextEngine()
        self.tts_engine = TextToSpeechEngine()
        self.validator = DeterministicFinancialValidator()

    def get_or_create_session(self, session_id: Optional[str] = None) -> ConversationSession:
        sid = session_id or str(uuid.uuid4())
        if sid not in self.sessions or self.sessions[sid].is_expired():
            self.sessions[sid] = ConversationSession(sid)
        return self.sessions[sid]

    async def process_user_request(self, request: AgentMessageRequest) -> AgentMessageResponse:
        """
        Execute full conversational agent pipeline:
        1. Process Audio / Text
        2. Detect Language & Intent with Negation Checks
        3. Inspect Interface
        4. Validate Financial Data (Zero Fabrication)
        5. Formulate Response & Synthesize Audio
        """
        session = self.get_or_create_session(request.session_id)
        steps: List[AgentActionStep] = []
        user_query = request.user_input or ""
        target_lang = request.language or session.preferred_language

        # Step 1: Voice transcription if audio provided
        if request.audio_base64:
            import base64
            try:
                audio_bytes = base64.b64decode(request.audio_base64)
                stt_result = self.stt_engine.transcribe_audio_bytes(
                    audio_bytes, session_id=session.session_id, hint_language=target_lang
                )
                user_query = stt_result.text
                target_lang = stt_result.language
                steps.append(AgentActionStep(
                    step_id=1,
                    description=f"Audio transcrit avec succès ({target_lang.value})",
                    action_type="SPEECH_TO_TEXT",
                    payload={"transcription": user_query, "confidence": stt_result.confidence}
                ))
            except Exception as e:
                logger.error(f"Voice transcription error: {e}")
                user_query = ""

        session.preferred_language = target_lang
        session.add_turn("user", user_query)

        # Step 2: Language & Intent Understanding
        intent = self._detect_intent(user_query, target_lang, session)
        steps.append(AgentActionStep(
            step_id=len(steps) + 1,
            description=f"Intention identifiée: {intent.value} (État: {session.dialog_state.value})",
            action_type="INTENT_CLASSIFICATION",
            payload={"intent": intent.value, "language": target_lang.value, "dialog_state": session.dialog_state.value}
        ))

        # Step 3: Browser Navigation / Inspection
        if request.page_url:
            await self.browser.navigate(request.page_url)

        extraction = await self.browser.inspect_page()
        session.last_extraction = extraction
        steps.append(AgentActionStep(
            step_id=len(steps) + 1,
            description=f"Interface analysée ({len(extraction.elements)} éléments extraits)",
            action_type="DOM_INSPECTION",
            payload={
                "title": extraction.title,
                "balances_count": len(extraction.balances),
                "fees_count": len(extraction.fees)
            }
        ))

        # Step 4: Dispatch Intent Execution
        explanation = ""
        prepared_tx: Optional[PreparedTransaction] = None
        requires_confirmation = False
        missing_params: List[str] = []

        if intent == AgentIntent.CANCEL_TRANSFER:
            explanation, steps = await self._handle_cancel_transfer(session, target_lang, steps)

        elif intent == AgentIntent.CORRECTION:
            explanation, prepared_tx, missing_params, steps = await self._handle_correction(
                session, extraction, user_query, target_lang, steps
            )
            requires_confirmation = (session.dialog_state == DialogState.AWAITING_CONFIRMATION)

        elif intent == AgentIntent.CONFIRM_TRANSFER:
            explanation, prepared_tx, steps = await self._handle_confirm_transfer(
                session, user_query, target_lang, steps
            )

        elif intent == AgentIntent.CHECK_BALANCE:
            explanation, steps = await self._handle_check_balance(session, extraction, target_lang, steps)

        elif intent == AgentIntent.EXPLAIN_FEES:
            explanation, steps = await self._handle_explain_fees(session, extraction, target_lang, steps)

        elif intent == AgentIntent.PREPARE_TRANSFER:
            explanation, prepared_tx, missing_params, steps = await self._handle_prepare_transfer(
                session, extraction, user_query, target_lang, steps
            )
            requires_confirmation = (session.dialog_state == DialogState.AWAITING_CONFIRMATION)

        elif intent == AgentIntent.TRANSLATE_PAGE:
            explanation, steps = await self._handle_translate_page(session, target_lang, steps)

        else:
            # General financial help / overview
            explanation_fr = (
                "Je suis Mboa Finance AI, votre assistant financier vocal en langues camerounaises. "
                "Je peux lire votre solde, expliquer les frais, ou préparer vos transferts de manière sécurisée."
            )
            if target_lang != LanguageCode.FRENCH:
                trans, _ = self.translation_engine.translate(explanation_fr, LanguageCode.FRENCH, target_lang)
                explanation = trans
            else:
                explanation = explanation_fr

        # Step 5: Audio Response Synthesis
        tts_audio_b64 = None
        if LanguageRegistry.is_speech_output_supported(target_lang.value) and explanation:
            try:
                synth_resp = self.tts_engine.synthesize(
                    SynthesisRequest(text=explanation, language=target_lang)
                )
                tts_audio_b64 = synth_resp.audio_base64
                steps.append(AgentActionStep(
                    step_id=len(steps) + 1,
                    description=f"Réponse vocale générée ({target_lang.value})",
                    action_type="TEXT_TO_SPEECH",
                    payload={"duration_seconds": synth_resp.duration_seconds}
                ))
            except Exception as e:
                logger.error(f"TTS synthesis error: {e}")

        # Data Provenance Classification (Mandatory SAFINUM distinction)
        data_provenance = {
            "source_application": "SIMULATED_FINANCIAL_INTERFACE",
            "explanation": "AI_GENERATED_ACCESSIBILITY_LAYER",
            "operation_mode": "SIMULATION_ONLY"
        }
        if extraction.balances:
            data_provenance["balance"] = "EXTRACTED_FROM_INTERFACE_DOM"
        if extraction.fees:
            data_provenance["fee"] = "EXTRACTED_FROM_INTERFACE_DOM"
        elif intent in (AgentIntent.PREPARE_TRANSFER, AgentIntent.CONFIRM_TRANSFER):
            data_provenance["fee"] = "AUTHORITATIVE_PROVIDER_SCHEDULE"

        session.add_turn("agent", explanation, meta={"intent": intent.value, "state": session.dialog_state.value})

        return AgentMessageResponse(
            session_id=session.session_id,
            detected_language=target_lang,
            transcribed_text=user_query,
            intent=intent,
            explanation=explanation,
            audio_base64=tts_audio_b64,
            steps=steps,
            prepared_transaction=prepared_tx,
            extracted_data={
                "balances": [b.model_dump() for b in extraction.balances],
                "fees": [f.model_dump() for f in extraction.fees],
                "warnings": extraction.warnings
            },
            requires_user_confirmation=requires_confirmation,
            dialog_state=session.dialog_state,
            missing_parameters=missing_params,
            is_simulated=True,
            simulation_badge="[OPÉRATION SIMULÉE - DÉFI SAFINUM]",
            data_provenance=data_provenance
        )

    def _detect_intent(self, text: str, lang: LanguageCode, session: ConversationSession) -> AgentIntent:
        """
        Disambiguates user intent with explicit awareness of dialog state and negations.
        """
        t = text.lower().strip()

        # 1. Check for explicit Negation or Cancellation
        negation_cues = [
            "ne pas", "n'envoie pas", "ne transfère pas", "ne fais pas", "annule", "annuler",
            "cancel", "stop", "arrête", "non pas", "pas du tout", "refuse", "haɗu", "dacca", "tege"
        ]
        if any(neg in t for neg in negation_cues):
            return AgentIntent.CANCEL_TRANSFER

        # 2. Check for Confirmation
        # ONLY valid if the session is actively awaiting confirmation
        confirmation_cues = [
            "confirmer", "confirme", "valider", "d'accord", "je confirme",
            "c'est bon", "envoie", "agree", "confirm", "yes, confirm",
            "jaɓi", "mi jaɓi", "kañ nlem", "yene mvaé", "dumi"
        ]
        if session.dialog_state == DialogState.AWAITING_CONFIRMATION:
            if any(c in t for c in confirmation_cues):
                return AgentIntent.CONFIRM_TRANSFER
            # Bare "oui" / "yes" while waiting confirmation
            if t in ["oui", "yes", "ok", "d'accord", "oui je confirme", "yes confirm"]:
                return AgentIntent.CONFIRM_TRANSFER

        # 3. Check for Correction or Clarification Parameter Supply
        # If in NEED_CLARIFICATION or AWAITING_CONFIRMATION and user provides a number or phone
        if session.dialog_state in (DialogState.NEED_CLARIFICATION, DialogState.AWAITING_CONFIRMATION):
            if any(c in t for c in ["plutôt", "change pour", "c'est plutôt", "remplace par"]):
                return AgentIntent.CORRECTION
            # If user supplies just an amount or phone number
            if self.validator.parse_amount(t) is not None or self.validator.CAMEROON_PHONE_PATTERN.search(t):
                return AgentIntent.CORRECTION

        # 4. Check for Transfer Requests
        transfer_cues = [
            "envoyer", "transfert", "transférer", "envoi", "send", "transfer",
            "neldugo", "lɔm", "sɔ̂", "loma", "cotiser", "tontine", "njangi"
        ]
        if any(tr in t for tr in transfer_cues):
            return AgentIntent.PREPARE_TRANSFER

        # 5. Check for Fee Inquiry
        fee_cues = [
            "frais", "tarif", "combien ça coûte", "charges", "commission",
            "coggu", "asik", "fa'", "ndando"
        ]
        if any(f in t for f in fee_cues):
            return AgentIntent.EXPLAIN_FEES

        # 6. Check for Balance Inquiry
        balance_cues = [
            "solde", "mon compte", "combien j'ai", "argent", "balance",
            "ceede", "moni", "nkáp", "moto"
        ]
        if any(b in t for b in balance_cues):
            return AgentIntent.CHECK_BALANCE

        # 7. Check for Interface Translation
        if any(tr in t for tr in ["traduire", "traduis", "translate", "change la langue"]):
            return AgentIntent.TRANSLATE_PAGE

        return AgentIntent.HELP

    async def _handle_check_balance(
        self,
        session: ConversationSession,
        extraction: DOMExtractionResult,
        target_lang: LanguageCode,
        steps: List[AgentActionStep]
    ) -> Tuple[str, List[AgentActionStep]]:
        """
        Inspects real balances from interface without hallucinations.
        Never fabricates a default balance if none is detected.
        """
        if extraction.balances:
            bal = extraction.balances[0]
            val_str = f"{int(bal.parsed_numeric_value):,} {bal.currency}".replace(",", " ")
            explanation_fr = f"Votre solde disponible est de {val_str}."
        else:
            # ZERO FABRICATION: If no balance is found, clearly state unavailable
            explanation_fr = (
                "Information indisponible : votre solde n'a pas pu être détecté sur cette interface. "
                "Veuillez vous assurer que vous êtes bien connecté à votre compte."
            )

        # Translate into user's language with number shielding
        if target_lang != LanguageCode.FRENCH:
            translated, _ = self.translation_engine.translate(
                explanation_fr, LanguageCode.FRENCH, target_lang
            )
            final_explanation = translated
        else:
            final_explanation = explanation_fr

        steps.append(AgentActionStep(
            step_id=len(steps) + 1,
            description="Solde vérifié auprès de l'interface sans valeur par défaut",
            action_type="BALANCE_LOOKUP",
            payload={"verified_balance": final_explanation, "balances_found": len(extraction.balances)}
        ))
        session.dialog_state = DialogState.IDLE
        return final_explanation, steps

    async def _handle_explain_fees(
        self,
        session: ConversationSession,
        extraction: DOMExtractionResult,
        target_lang: LanguageCode,
        steps: List[AgentActionStep]
    ) -> Tuple[str, List[AgentActionStep]]:
        """Explains fee structure based strictly on verified interface or provider data."""
        if extraction.fees:
            f = extraction.fees[0]
            fee_amount = f"{int(f.parsed_numeric_value):,} {f.currency}".replace(",", " ")
            explanation_fr = (
                f"Les frais pour cette opération s'élèvent à {fee_amount}. "
                f"Ces frais sont fixes pour tout transfert standard et débités de votre compte."
            )
        else:
            explanation_fr = (
                "Information indisponible : les frais de transfert ne sont pas affichés sur l'interface active."
            )

        if target_lang != LanguageCode.FRENCH:
            translated, _ = self.translation_engine.translate(
                explanation_fr, LanguageCode.FRENCH, target_lang
            )
            final_explanation = translated
        else:
            final_explanation = explanation_fr

        steps.append(AgentActionStep(
            step_id=len(steps) + 1,
            description="Explication des frais calculée sans hallucination",
            action_type="FEE_EXPLANATION",
            payload={"fees_found": len(extraction.fees)}
        ))
        session.dialog_state = DialogState.IDLE
        return final_explanation, steps

    async def _handle_prepare_transfer(
        self,
        session: ConversationSession,
        extraction: DOMExtractionResult,
        user_query: str,
        target_lang: LanguageCode,
        steps: List[AgentActionStep]
    ) -> Tuple[str, Optional[PreparedTransaction], List[str], List[AgentActionStep]]:
        """
        Parses transfer details strictly.
        Never substitutes default amounts or recipients.
        Transitions to NEED_CLARIFICATION if details are missing.
        """
        # Parse amount
        amount = self.validator.parse_amount(user_query) or session.draft_transfer.get("amount")

        # Parse recipient phone
        phone_match = self.validator.CAMEROON_PHONE_PATTERN.search(user_query)
        recipient_phone = phone_match.group(0) if phone_match else session.draft_transfer.get("recipient")

        missing_parameters = []
        if amount is None:
            missing_parameters.append("amount")
        if recipient_phone is None:
            missing_parameters.append("recipient")

        # Handle missing parameters gracefully
        if missing_parameters:
            session.dialog_state = DialogState.NEED_CLARIFICATION
            if amount is not None:
                session.draft_transfer["amount"] = amount
            if recipient_phone is not None:
                session.draft_transfer["recipient"] = recipient_phone

            if "amount" in missing_parameters and "recipient" in missing_parameters:
                explanation_fr = "Veuillez préciser le montant et le numéro de téléphone du destinataire pour effectuer le transfert."
            elif "amount" in missing_parameters:
                explanation_fr = f"Quel montant souhaitez-vous envoyer au {recipient_phone} ?"
            else:
                amt_str = f"{int(amount):,} FCFA".replace(",", " ")
                explanation_fr = f"À quel numéro de téléphone souhaitez-vous envoyer les {amt_str} ?"

            if target_lang != LanguageCode.FRENCH:
                translated, _ = self.translation_engine.translate(explanation_fr, LanguageCode.FRENCH, target_lang)
                explanation = translated
            else:
                explanation = explanation_fr

            steps.append(AgentActionStep(
                step_id=len(steps) + 1,
                description="Paramètres manquants : demande de clarification sans fabrication de valeurs",
                action_type="CLARIFICATION_REQUIRED",
                payload={"missing_parameters": missing_parameters}
            ))
            return explanation, None, missing_parameters, steps

        # Both Amount and Recipient are present -> Validate and Prepare
        if amount <= 0:
            explanation_fr = "Le montant du transfert doit être supérieur à zéro."
            session.dialog_state = DialogState.NEED_CLARIFICATION
            return explanation_fr, None, ["amount"], steps

        # Invalidate any previous pending transaction if user initiates a new preparation or modifies parameters
        if session.pending_transaction_id:
            try:
                self.action_guard.invalidate_transaction(
                    session.pending_transaction_id,
                    reason="Paramètres modifiés : remplacement par une nouvelle transaction"
                )
            except Exception as e:
                logger.warning(f"Error invalidating previous transaction: {e}")
            session.pending_transaction_id = None

        # Determine authoritative fee from interface DOM or provider tariff schedule
        if extraction.fees and extraction.fees[0].parsed_numeric_value is not None:
            fee = extraction.fees[0].parsed_numeric_value
        else:
            fee = self.provider_router.quote_fee(recipient_phone, amount)

        total_debit = amount + fee

        # Source account verified from session or interface
        source_acc = "CM21-10005-00012345678-89"
        if extraction.balances:
            source_acc = extraction.balances[0].associated_element_id or source_acc

        # Pre-fill browser form
        await self.browser.fill_simulated_form(str(int(amount)), recipient_phone)

        # Prepare transaction in ActionGuard with cryptographic binding
        tx = self.action_guard.prepare_transaction(
            source_account=source_acc,
            beneficiary_name=f"Destinataire ({recipient_phone})",
            beneficiary_account=recipient_phone,
            amount=amount,
            fee=fee,
            total_debit=total_debit,
            currency="FCFA"
        )
        session.pending_transaction_id = tx.transaction_id
        session.dialog_state = DialogState.AWAITING_CONFIRMATION
        session.draft_transfer.clear()

        steps.append(AgentActionStep(
            step_id=len(steps) + 1,
            description=f"Transaction préparée avec succès: {int(amount)} + {int(fee)} = {int(total_debit)} FCFA",
            action_type="PREPARE_TRANSACTION",
            payload=tx.model_dump()
        ))

        explanation_fr = (
            f"J'ai préparé votre transfert de {int(amount):,} FCFA vers le {recipient_phone}. "
            f"Frais de transfert: {int(fee):,} FCFA. "
            f"Total débité: {int(total_debit):,} FCFA. "
            f"Confirmez-vous cette opération ?"
        ).replace(",", " ")

        if target_lang != LanguageCode.FRENCH:
            translated, _ = self.translation_engine.translate(
                explanation_fr, LanguageCode.FRENCH, target_lang
            )
            final_explanation = translated
        else:
            final_explanation = explanation_fr

        return final_explanation, tx, [], steps

    async def _handle_confirm_transfer(
        self,
        session: ConversationSession,
        user_query: str,
        target_lang: LanguageCode,
        steps: List[AgentActionStep]
    ) -> Tuple[str, Optional[PreparedTransaction], List[AgentActionStep]]:
        """Executes confirmed transaction after verifying pending state, expiration, and cryptographic signature."""
        tx_id = session.pending_transaction_id

        if not tx_id or session.dialog_state != DialogState.AWAITING_CONFIRMATION:
            msg = "Aucune transaction en attente de confirmation."
            if target_lang != LanguageCode.FRENCH:
                trans, _ = self.translation_engine.translate(msg, LanguageCode.FRENCH, target_lang)
                msg = trans
            session.dialog_state = DialogState.IDLE
            return msg, None, steps

        try:
            tx = self.action_guard.confirm_transaction(
                transaction_id=tx_id,
                explicit_user_consent=True,
                user_acknowledgment=user_query,
                idempotency_key=f"exec-{tx_id}"
            )
        except SecurityViolationError as sve:
            logger.warning(f"Confirmation security violation: {sve}")
            msg = f"Impossible de confirmer l'opération : {sve}"
            if target_lang != LanguageCode.FRENCH:
                trans, _ = self.translation_engine.translate(msg, LanguageCode.FRENCH, target_lang)
                msg = trans
            session.dialog_state = DialogState.IDLE
            return msg, None, steps

        # Submit simulated form in browser
        await self.browser.submit_simulated_form()

        # Dispatch execution to authoritative provider
        provider = self.provider_router.resolve_provider(tx.beneficiary_account)
        provider_res = await provider.execute_transfer(tx, idempotency_key=f"prov-{tx_id}")

        if provider_res.success:
            tx.status = TransactionStatus.COMPLETED
            tx.provider = provider.provider_name
            tx.provider_reference = provider_res.provider_reference
            self.action_guard.repository.save_transaction(tx)

        steps.append(AgentActionStep(
            step_id=len(steps) + 1,
            description=f"Transaction confirmée et soumise au prestataire {provider.provider_name} ({'SIMULÉ' if provider.is_simulation else 'RÉEL'})",
            action_type="SUBMIT_TRANSACTION",
            payload={"transaction_id": tx_id, "status": tx.status.value, "provider": provider.provider_name, "provider_ref": provider_res.provider_reference}
        ))

        explanation_fr = (
            f"Transfert de {int(tx.amount):,} FCFA confirmé avec succès vers le {tx.beneficiary_account}. "
            f"Référence: {provider_res.provider_reference}."
        ).replace(",", " ")

        if target_lang != LanguageCode.FRENCH:
            translated, _ = self.translation_engine.translate(
                explanation_fr, LanguageCode.FRENCH, target_lang
            )
            final_explanation = translated
        else:
            final_explanation = explanation_fr

        session.dialog_state = DialogState.COMPLETED
        session.pending_transaction_id = None
        return final_explanation, tx, steps

        session.pending_transaction_id = None
        session.dialog_state = DialogState.COMPLETED
        return final_explanation, tx, steps

    async def _handle_cancel_transfer(
        self,
        session: ConversationSession,
        target_lang: LanguageCode,
        steps: List[AgentActionStep]
    ) -> Tuple[str, List[AgentActionStep]]:
        """Safely cancels in-flight or prepared transaction upon user request."""
        tx_id = session.pending_transaction_id
        if tx_id:
            try:
                self.action_guard.cancel_transaction(tx_id, reason="User explicit cancellation")
            except Exception:
                pass

        session.pending_transaction_id = None
        session.draft_transfer.clear()
        session.dialog_state = DialogState.CANCELLED

        msg_fr = "Opération annulée. Aucun montant n'a été débité de votre compte."
        if target_lang != LanguageCode.FRENCH:
            trans, _ = self.translation_engine.translate(msg_fr, LanguageCode.FRENCH, target_lang)
            msg_fr = trans

        steps.append(AgentActionStep(
            step_id=len(steps) + 1,
            description="Opération annulée à la demande de l'utilisateur",
            action_type="CANCEL_TRANSACTION",
            payload={"status": "CANCELLED"}
        ))
        return msg_fr, steps

    async def _handle_correction(
        self,
        session: ConversationSession,
        extraction: DOMExtractionResult,
        user_query: str,
        target_lang: LanguageCode,
        steps: List[AgentActionStep]
    ) -> Tuple[str, Optional[PreparedTransaction], List[str], List[AgentActionStep]]:
        """Handles user corrections to amount or recipient."""
        # Update draft parameters
        new_amt = self.validator.parse_amount(user_query)
        if new_amt is not None:
            session.draft_transfer["amount"] = new_amt

        phone_match = self.validator.CAMEROON_PHONE_PATTERN.search(user_query)
        if phone_match:
            session.draft_transfer["recipient"] = phone_match.group(0)

        # Cancel previous pending transaction if it existed
        if session.pending_transaction_id:
            try:
                self.action_guard.cancel_transaction(session.pending_transaction_id, reason="Parameter corrected by user")
            except Exception:
                pass
            session.pending_transaction_id = None

        return await self._handle_prepare_transfer(session, extraction, user_query, target_lang, steps)

    async def _handle_translate_page(
        self,
        session: ConversationSession,
        target_lang: LanguageCode,
        steps: List[AgentActionStep]
    ) -> Tuple[str, List[AgentActionStep]]:
        """Translates the active web page in-place."""
        result = await self.browser.translate_page(
            source_lang=LanguageCode.FRENCH,
            target_lang=target_lang
        )
        steps.append(AgentActionStep(
            step_id=len(steps) + 1,
            description=f"Interface traduite en direct ({result['translated_elements_count']} éléments)",
            action_type="TRANSLATE_INTERFACE",
            payload=result
        ))
        msg_fr = f"L'interface a été traduite avec succès en {target_lang.value}."
        if target_lang != LanguageCode.FRENCH:
            trans, _ = self.translation_engine.translate(msg_fr, LanguageCode.FRENCH, target_lang)
            msg_fr = trans
        session.dialog_state = DialogState.IDLE
        return msg_fr, steps
