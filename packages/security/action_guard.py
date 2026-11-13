"""
Two-Phase Action Guard and Security Manager for Mboa Finance AI.
Strictly separates PREPARATION from CONFIRMATION/EXECUTION.
Prohibits autonomous execution of consequential actions.
Enforces:
- Cryptographic HMAC-SHA256 parameter binding with explicit expiration (120s).
- Idempotency key tracking for deduplication and replay attack prevention.
- Automatic PII masking in audit trails and system logs.
- Atomic state transitions backed by durable SQLite/PostgreSQL persistence.
"""

import os
import re
import time
import uuid
import hmac
import hashlib
import logging
from typing import Dict, List, Optional, Any
from packages.shared_schemas.mboa_schemas import (
    PreparedTransaction,
    TransactionStatus,
    VerificationStatus,
    VerificationReport
)
from packages.financial_validation.validator import DeterministicFinancialValidator
from packages.storage.repository import DatabaseRepository, get_repository

logger = logging.getLogger("mboa.security.action_guard")


class SecurityViolationError(Exception):
    """Raised when an operation violates security boundaries."""
    pass


class ActionGuard:
    """
    Production-grade Two-Phase Action Guard.
    Manages transaction lifecycle with cryptographic integrity, replay defense,
    and durable tamper-evident audit trails.
    """

    TRANSACTION_EXPIRY_SECONDS = 120.0  # 2 minutes strictly enforced validity

    def __init__(self, repository: Optional[DatabaseRepository] = None, secret_key: Optional[str] = None):
        self.repository = repository or get_repository()
        # Secret key for HMAC parameter binding
        self._secret_key = (
            secret_key or os.environ.get("MBOA_SECRET_KEY", "mboa_dev_secret_key_change_in_production_998877")
        ).encode("utf-8")
        self._prepared_transactions: Dict[str, PreparedTransaction] = {}
        self._audit_log: List[Dict] = []
        self._rate_limits: Dict[str, List[float]] = {}
        self._active_locks: set = set()

    def check_rate_limit(self, client_id: str, max_requests: int = 30, window_seconds: float = 60.0) -> None:
        """
        Sliding-window rate limiter preventing brute-force or denial-of-service abuse.
        """
        now = time.time()
        timestamps = self._rate_limits.setdefault(client_id, [])
        # Prune old timestamps
        cutoff = now - window_seconds
        self._rate_limits[client_id] = [t for t in timestamps if t > cutoff]

        if len(self._rate_limits[client_id]) >= max_requests:
            logger.warning(f"Rate limit exceeded for client {client_id}: {len(self._rate_limits[client_id])} requests in {window_seconds}s")
            raise SecurityViolationError(f"Limite de requêtes atteinte ({max_requests} par minute). Veuillez patienter.")

        self._rate_limits[client_id].append(now)

    def acquire_concurrency_lock(self, resource_id: str) -> None:
        """Prevents race condition double-execution on concurrent confirmation requests."""
        if resource_id in self._active_locks:
            logger.warning(f"Concurrent operation blocked for resource {resource_id}")
            raise SecurityViolationError("Une opération concurrente est déjà en cours d'exécution pour cette transaction.")
        self._active_locks.add(resource_id)

    def release_concurrency_lock(self, resource_id: str) -> None:
        """Releases concurrency lock after operation concludes."""
        self._active_locks.discard(resource_id)

    def invalidate_transaction(self, transaction_id: str, reason: str = "Paramètres de transaction modifiés") -> PreparedTransaction:
        """
        Explicitly invalidates and cancels a pending authorization if details change.
        Mandatory SAFINUM rule: If any transaction detail changes after preparation,
        invalidate the previous authorization and require a new confirmation.
        """
        tx = self.get_transaction(transaction_id)
        if not tx:
            raise SecurityViolationError(f"Transaction ID {transaction_id} introuvable.")

        tx.status = TransactionStatus.CANCELLED
        self._prepared_transactions[transaction_id] = tx
        self.repository.save_transaction(tx)
        self._log_audit_event("TRANSACTION_INVALIDATED", tx.model_dump(), f"Invalidated: {reason}")
        logger.info(f"Transaction {transaction_id} invalidated: {reason}")
        return tx

    def _compute_hmac(
        self,
        tx_id: str,
        source_account: str,
        beneficiary_account: str,
        amount: float,
        fee: float,
        total_debit: float,
        currency: str,
        expires_at: float
    ) -> str:
        """Computes HMAC-SHA256 binding all consequential parameters to prevent tampering."""
        message = f"{tx_id}|{source_account}|{beneficiary_account}|{amount:.2f}|{fee:.2f}|{total_debit:.2f}|{currency}|{expires_at:.2f}".encode("utf-8")
        return hmac.new(self._secret_key, message, hashlib.sha256).hexdigest()

    @classmethod
    def mask_pii(cls, data: Any) -> Any:
        """
        Recursively masks Personally Identifiable Information (PII) including
        phone numbers, account identifiers, full names, and secrets.
        """
        if isinstance(data, dict):
            masked = {}
            for k, v in data.items():
                k_lower = k.lower()
                if any(sec in k_lower for sec in ("pin", "secret", "password", "token", "auth")):
                    masked[k] = "[REDACTED_SECRET]"
                elif "phone" in k_lower or "recipient" in k_lower or "beneficiary_account" in k_lower:
                    masked[k] = cls._mask_identifier(str(v))
                elif "name" in k_lower and isinstance(v, str):
                    masked[k] = cls._mask_name(v)
                else:
                    masked[k] = cls.mask_pii(v)
            return masked
        elif isinstance(data, list):
            return [cls.mask_pii(item) for item in data]
        elif isinstance(data, str):
            return cls._mask_text_entities(data)
        return data

    @classmethod
    def _mask_identifier(cls, identifier: str) -> str:
        """Masks phone numbers and account numbers: e.g. 699001122 -> 699***122."""
        clean = identifier.strip()
        if len(clean) >= 9:
            return clean[:3] + "***" + clean[-3:]
        elif len(clean) > 4:
            return clean[:2] + "***" + clean[-1:]
        return "***"

    @classmethod
    def _mask_name(cls, name: str) -> str:
        """Masks full names: Jean Paul -> J*** P***."""
        parts = name.strip().split()
        if not parts:
            return "***"
        return " ".join([f"{p[0]}***" if len(p) > 1 else p for p in parts])

    @classmethod
    def _mask_text_entities(cls, text: str) -> str:
        """Masks phone numbers in arbitrary text."""
        phone_pattern = re.compile(r'\b(?:\+?237\s*)?(6[25789]\d{7}|2[234]\d{7})\b')
        return phone_pattern.sub(lambda m: cls._mask_identifier(m.group(0)), text)

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
        warnings: Optional[List[str]] = None,
        idempotency_key: Optional[str] = None
    ) -> PreparedTransaction:
        """
        Phase 1: Prepare transaction, verify deterministic arithmetic, compute HMAC signature,
        enforce 120s validity, and check idempotency.
        Does NOT execute or debit any funds.
        """
        # Idempotency check
        if idempotency_key:
            existing = self.repository.get_idempotency_record(idempotency_key)
            if existing and existing.get("transaction_id"):
                cached_tx = self.get_transaction(existing["transaction_id"])
                if cached_tx:
                    logger.info(f"Idempotency hit for key {idempotency_key}, returning existing tx {cached_tx.transaction_id}")
                    return cached_tx

        tx_id = f"TX-MBOA-{uuid.uuid4().hex[:8].upper()}"
        now = time.time()
        expires_at = now + self.TRANSACTION_EXPIRY_SECONDS

        # Compute tamper-proof cryptographic signature
        signature = self._compute_hmac(
            tx_id=tx_id,
            source_account=source_account,
            beneficiary_account=beneficiary_account,
            amount=amount,
            fee=fee,
            total_debit=total_debit,
            currency=currency,
            expires_at=expires_at
        )

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
                "Opération sécurisée par MboaFlow Action Guard",
                "Délai d'exécution: Immédiat",
                "Frais certifiés conformes à la grille tarifaire"
            ],
            warnings=warnings or [
                "Attention: Vérifiez le numéro du destinataire avant confirmation.",
                "Ne communiquez jamais votre code secret PIN à qui que ce soit."
            ],
            status=TransactionStatus.PREPARED,
            verification_status=VerificationStatus.UNVERIFIED,
            verification_notes=[],
            simulated=True,
            prepared_at=now,
            signature=signature,
            expires_at=expires_at,
            idempotency_key=idempotency_key
        )

        # Run deterministic validation
        report: VerificationReport = DeterministicFinancialValidator.validate_prepared_transaction(tx)
        tx.verification_status = report.status
        tx.verification_notes = report.notes

        if not report.is_valid:
            logger.warning(f"Transaction {tx_id} failed deterministic verification: {report.notes}")
            tx.status = TransactionStatus.REJECTED
            self._log_audit_event("TRANSACTION_REJECTED", tx.model_dump(), f"Validation failed: {report.notes}")
            self.repository.save_transaction(tx)
            raise SecurityViolationError(f"Transaction rejected by Financial Integrity Engine: {'; '.join(report.notes)}")

        tx.status = TransactionStatus.PENDING_CONFIRMATION
        self._prepared_transactions[tx_id] = tx
        self.repository.save_transaction(tx)

        if idempotency_key:
            self.repository.save_idempotency_record(
                key=idempotency_key,
                action_type="PREPARE_TRANSACTION",
                transaction_id=tx_id,
                status="PREPARED",
                response=tx.model_dump()
            )

        self._log_audit_event("TRANSACTION_PREPARED", tx.model_dump(), "Pending explicit user confirmation")
        return tx

    def confirm_transaction(
        self,
        transaction_id: str,
        explicit_user_consent: bool,
        user_acknowledgment: Optional[str] = None,
        idempotency_key: Optional[str] = None
    ) -> PreparedTransaction:
        """
        Phase 2: Explicit User Confirmation.
        Requires explicit user consent; validates expiration, verifies cryptographic HMAC signature,
        re-verifies arithmetic, and prevents double execution.
        """
        if idempotency_key:
            existing = self.repository.get_idempotency_record(idempotency_key)
            if existing and existing.get("transaction_id"):
                cached_tx = self.get_transaction(existing["transaction_id"])
                if cached_tx and cached_tx.status in (TransactionStatus.CONFIRMED, TransactionStatus.COMPLETED):
                    logger.info(f"Idempotency hit for confirmation key {idempotency_key}, returning cached confirmation")
                    return cached_tx

        tx = self.get_transaction(transaction_id)
        if not tx:
            raise SecurityViolationError(f"Transaction ID {transaction_id} not found or expired.")

        # Concurrency Lock: Prevents race condition double execution
        self.acquire_concurrency_lock(transaction_id)
        try:
            # Atomic status check
            if tx.status == TransactionStatus.CONFIRMED or tx.status == TransactionStatus.COMPLETED:
                logger.info(f"Transaction {transaction_id} is already confirmed.")
                return tx

            if tx.status != TransactionStatus.PENDING_CONFIRMATION:
                raise SecurityViolationError(f"Transaction {transaction_id} is in status {tx.status}, cannot confirm.")

            # Check expiration (120 seconds limit)
            now = time.time()
            if tx.expires_at and now > tx.expires_at:
                tx.status = TransactionStatus.CANCELLED
                self.repository.save_transaction(tx)
                self._log_audit_event("TRANSACTION_EXPIRED", tx.model_dump(), f"Expired by {now - tx.expires_at:.1f}s")
                raise SecurityViolationError(f"Transaction {transaction_id} has expired (validity exceeded {self.TRANSACTION_EXPIRY_SECONDS}s).")

            # Cryptographic signature validation
            expected_sig = self._compute_hmac(
                tx_id=tx.transaction_id,
                source_account=tx.source_account,
                beneficiary_account=tx.beneficiary_account,
                amount=tx.amount,
                fee=tx.fee,
                total_debit=tx.total_debit,
                currency=tx.currency,
                expires_at=tx.expires_at or 0.0
            )
            if not hmac.compare_digest(tx.signature or "", expected_sig):
                tx.status = TransactionStatus.REJECTED
                self.repository.save_transaction(tx)
                self._log_audit_event("TRANSACTION_TAMPER_DETECTED", tx.model_dump(), "Cryptographic signature mismatch")
                raise SecurityViolationError("Security breach: Transaction parameters tampered with prior to confirmation.")

            if not explicit_user_consent:
                tx.status = TransactionStatus.CANCELLED
                self.repository.save_transaction(tx)
                self._log_audit_event("TRANSACTION_CANCELLED", tx.model_dump(), "User declined confirmation")
                return tx

            # Re-verify deterministic arithmetic right before execution
            report = DeterministicFinancialValidator.validate_prepared_transaction(tx)
            if not report.is_valid:
                tx.status = TransactionStatus.REJECTED
                self.repository.save_transaction(tx)
                self._log_audit_event("TRANSACTION_ARITHMETIC_TAMPER", tx.model_dump(), "Arithmetic discrepancy at confirmation")
                raise SecurityViolationError("Financial values altered prior to confirmation.")

            tx.status = TransactionStatus.CONFIRMED
            tx.confirmed_at = now
            self._prepared_transactions[transaction_id] = tx
            self.repository.save_transaction(tx)

            if idempotency_key:
                self.repository.save_idempotency_record(
                    key=idempotency_key,
                    action_type="CONFIRM_TRANSACTION",
                    transaction_id=tx.transaction_id,
                    status="CONFIRMED",
                    response=tx.model_dump()
                )

            self._log_audit_event(
                "TRANSACTION_CONFIRMED",
                tx.model_dump(),
                f"User acknowledged: {user_acknowledgment or 'EXPLICIT_CONFIRMATION'}"
            )
            return tx
        finally:
            self.release_concurrency_lock(transaction_id)

    def cancel_transaction(self, transaction_id: str, reason: str = "User cancelled") -> PreparedTransaction:
        """Cancel an in-flight prepared transaction safely."""
        tx = self.get_transaction(transaction_id)
        if not tx:
            raise SecurityViolationError(f"Transaction {transaction_id} not found.")

        if tx.status in (TransactionStatus.CONFIRMED, TransactionStatus.COMPLETED):
            raise SecurityViolationError(f"Cannot cancel transaction {transaction_id} in state {tx.status}")

        tx.status = TransactionStatus.CANCELLED
        self._prepared_transactions[transaction_id] = tx
        self.repository.save_transaction(tx)
        self._log_audit_event("TRANSACTION_CANCELLED", tx.model_dump(), reason)
        return tx

    def get_transaction(self, transaction_id: str) -> Optional[PreparedTransaction]:
        """Retrieves transaction from memory cache or falls back to database repository."""
        if transaction_id in self._prepared_transactions:
            return self._prepared_transactions[transaction_id]
        tx = self.repository.get_transaction(transaction_id)
        if tx:
            self._prepared_transactions[transaction_id] = tx
        return tx

    def _log_audit_event(
        self,
        event_type: str,
        payload: Dict,
        note: str,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        masked_payload = self.mask_pii(payload)
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "session_id": session_id,
            "correlation_id": correlation_id,
            "payload": masked_payload,
            "note": note
        }
        self._audit_log.append(event)
        try:
            self.repository.log_audit_event(
                event_type=event_type,
                masked_payload=masked_payload,
                note=note,
                session_id=session_id,
                correlation_id=correlation_id
            )
        except Exception as e:
            logger.error(f"Failed to persist audit log to repository: {e}")
        logger.info(f"AUDIT_EVENT: {event_type} - {note}")

    def get_audit_trail(self, limit: int = 100) -> List[Dict]:
        """Returns durable PII-masked audit log trail."""
        repo_logs = self.repository.get_audit_trail(limit=limit)
        if repo_logs:
            return repo_logs
        return list(self._audit_log)[-limit:]
