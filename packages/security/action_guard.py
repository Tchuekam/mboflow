"""
Two-Phase Action Guard and Security Manager for Mboa Finance AI.
Strictly separates PREPARATION from CONFIRMATION/EXECUTION.
Prohibits autonomous execution of consequential actions.
Enforces audit logging, explicit confirmation checks, and safe rollback states.
"""

import time
import uuid
import logging
from typing import Dict, List, Optional
from packages.shared_schemas.mboa_schemas import (
    PreparedTransaction,
    TransactionStatus,
    VerificationStatus,
    VerificationReport
)
from packages.financial_validation.validator import DeterministicFinancialValidator

logger = logging.getLogger("mboa.security.action_guard")


class SecurityViolationError(Exception):
    """Raised when an operation violates security boundaries."""
    pass


class ActionGuard:
    """
    Two-Phase Action Guard.
    Maintains active prepared transactions in memory, ensures deterministic validation
    before any presentation to the user, and strictly requires explicit user confirmation
    before dispatching simulated submission.
    """

    def __init__(self):
        self._prepared_transactions: Dict[str, PreparedTransaction] = {}
        self._audit_log: List[Dict] = []

    def prepare_transaction(
        self,
        source_account: str,
        beneficiary_name: str,
        beneficiary_account: str,
        amount: float,
        fee: float,
        total_debit: float,
        currency: str = "FCFA",
        conditions: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None
    ) -> PreparedTransaction:
        """
        Phase 1: Prepare transaction and run deterministic verification.
        Does NOT execute or debit any funds.
        """
        tx_id = f"TX-SIM-{uuid.uuid4().hex[:8].upper()}"
        now = time.time()

        tx = PreparedTransaction(
            transaction_id=tx_id,
            source_account=source_account,
            beneficiary_name=beneficiary_name,
            beneficiary_account=beneficiary_account,
            amount=amount,
            fee=fee,
            total_debit=total_debit,
            currency=currency,
            conditions=conditions or [
                "Opération simulée (SAFINUM Challenge Prototype)",
                "Délai d'exécution estimé: Immédiat",
                "Frais calculés selon la grille tarifaire standard"
            ],
            warnings=warnings or [
                "Attention: Vérifiez le numéro du destinataire avant confirmation.",
                "Ne communiquez jamais votre code secret PIN à qui que ce soit."
            ],
            status=TransactionStatus.PREPARED,
            verification_status=VerificationStatus.UNVERIFIED,
            verification_notes=[],
            simulated=True,
            prepared_at=now
        )

        # Run deterministic validation
        report: VerificationReport = DeterministicFinancialValidator.validate_prepared_transaction(tx)
        tx.verification_status = report.status
        tx.verification_notes = report.notes

        if not report.is_valid:
            logger.warning(f"Transaction {tx_id} failed verification: {report.notes}")
            tx.status = TransactionStatus.REJECTED
            self._log_audit_event("TRANSACTION_REJECTED", tx.model_dump(), "Deterministic validation failed")
            raise SecurityViolationError(f"Transaction rejected by Financial Integrity Engine: {'; '.join(report.notes)}")

        tx.status = TransactionStatus.PENDING_CONFIRMATION
        self._prepared_transactions[tx_id] = tx

        self._log_audit_event("TRANSACTION_PREPARED", tx.model_dump(), "Pending explicit user confirmation")
        return tx

    def confirm_transaction(
        self,
        transaction_id: str,
        explicit_user_consent: bool,
        user_acknowledgment: Optional[str] = None
    ) -> PreparedTransaction:
        """
        Phase 2: Explicit User Confirmation.
        Requires explicit user consent; refuses to execute silently.
        """
        if transaction_id not in self._prepared_transactions:
            raise SecurityViolationError(f"Transaction ID {transaction_id} not found or expired.")

        tx = self._prepared_transactions[transaction_id]

        if tx.status != TransactionStatus.PENDING_CONFIRMATION:
            raise SecurityViolationError(f"Transaction {transaction_id} is in status {tx.status}, cannot confirm.")

        if not explicit_user_consent:
            tx.status = TransactionStatus.CANCELLED
            self._log_audit_event("TRANSACTION_CANCELLED", tx.model_dump(), "User declined confirmation")
            return tx

        # Re-verify deterministic math right before execution
        report = DeterministicFinancialValidator.validate_prepared_transaction(tx)
        if not report.is_valid:
            tx.status = TransactionStatus.REJECTED
            self._log_audit_event("TRANSACTION_TAMPER_DETECTED", tx.model_dump(), "Tamper detected at confirmation time")
            raise SecurityViolationError("Financial values altered prior to confirmation.")

        tx.status = TransactionStatus.CONFIRMED
        tx.confirmed_at = time.time()

        self._log_audit_event(
            "TRANSACTION_CONFIRMED_SIMULATED",
            tx.model_dump(),
            f"User acknowledged: {user_acknowledgment or 'EXPLICIT_VOICE_OR_CLICK_CONFIRMATION'}"
        )
        return tx

    def cancel_transaction(self, transaction_id: str, reason: str = "User cancelled") -> PreparedTransaction:
        """Cancel an in-flight prepared transaction safely."""
        if transaction_id not in self._prepared_transactions:
            raise SecurityViolationError(f"Transaction {transaction_id} not found.")

        tx = self._prepared_transactions[transaction_id]
        tx.status = TransactionStatus.CANCELLED
        self._log_audit_event("TRANSACTION_CANCELLED", tx.model_dump(), reason)
        return tx

    def get_transaction(self, transaction_id: str) -> Optional[PreparedTransaction]:
        return self._prepared_transactions.get(transaction_id)

    def _log_audit_event(self, event_type: str, payload: Dict, note: str):
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "payload": payload,
            "note": note
        }
        self._audit_log.append(event)
        logger.info(f"AUDIT_EVENT: {event_type} - {note}")

    def get_audit_trail(self) -> List[Dict]:
        return list(self._audit_log)

