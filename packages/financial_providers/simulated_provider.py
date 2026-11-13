"""
Simulated Banking Provider for Mboa Finance AI.
Strictly isolated sandbox provider for testing, prototyping, and demonstration.
All outputs are explicitly marked is_simulated=True.
"""

import uuid
import logging
from typing import Optional, Dict, Any
from .base import FinancialProviderBase, ProviderTransferResult
from packages.shared_schemas.mboa_schemas import PreparedTransaction

logger = logging.getLogger("mboa.providers.simulated")


class SimulatedBankingProvider(FinancialProviderBase):
    """
    Simulated banking implementation.
    Never debits real fiat currency; clearly reports simulated status.
    """

    def __init__(self, initial_accounts: Optional[Dict[str, float]] = None):
        self._accounts: Dict[str, float] = initial_accounts or {}
        self._transactions: Dict[str, ProviderTransferResult] = {}

    @property
    def provider_name(self) -> str:
        return "SIMULATED_BANK"

    @property
    def is_simulation(self) -> bool:
        return True

    async def get_balance(self, account_id: str) -> Optional[float]:
        """Returns account balance if explicitly registered, or None if unknown."""
        return self._accounts.get(account_id)

    def set_balance(self, account_id: str, balance: float):
        """Allows test setups to register an explicit account balance."""
        self._accounts[account_id] = float(balance)

    def quote_fee(self, amount: float) -> float:
        """Standard Cameroonian banking tier simulation fee."""
        if amount <= 0:
            return 0.0
        # Tiered fee schedule: 0.5% min 50 FCFA, max 500 FCFA
        calculated = amount * 0.005
        return round(max(50.0, min(calculated, 500.0)), 2)

    async def execute_transfer(
        self,
        transaction: PreparedTransaction,
        idempotency_key: str
    ) -> ProviderTransferResult:
        """Executes transfer in local simulated ledger."""
        src = transaction.source_account
        dest = transaction.beneficiary_account
        total = transaction.total_debit

        # Check if source account exists in ledger and has balance
        if src in self._accounts and self._accounts[src] < total:
            return ProviderTransferResult(
                success=False,
                provider_name=self.provider_name,
                provider_reference=f"SIM-FAIL-{uuid.uuid4().hex[:8].upper()}",
                status="FAILED_INSUFFICIENT_FUNDS",
                amount=transaction.amount,
                fee_charged=0.0,
                currency=transaction.currency,
                message=f"Solde insuffisant: solde disponible {self._accounts[src]} FCFA, débit requis {total} FCFA",
                is_simulated=True
            )

        # Debit source if present
        if src in self._accounts:
            self._accounts[src] -= total
        # Credit dest if present
        if dest in self._accounts:
            self._accounts[dest] += transaction.amount

        ref = f"SIM-TX-{uuid.uuid4().hex[:8].upper()}"
        res = ProviderTransferResult(
            success=True,
            provider_name=self.provider_name,
            provider_reference=ref,
            status="SUCCESS",
            amount=transaction.amount,
            fee_charged=transaction.fee,
            currency=transaction.currency,
            message="Transfert simulé complété avec succès dans l'environnement bac à sable.",
            raw_response={
                "idempotency_key": idempotency_key,
                "simulated_timestamp": transaction.prepared_at,
                "sender_remaining_balance": self._accounts.get(src)
            },
            is_simulated=True
        )
        self._transactions[ref] = res
        return res

    async def verify_transaction_status(self, provider_reference: str) -> ProviderTransferResult:
        if provider_reference in self._transactions:
            return self._transactions[provider_reference]
        return ProviderTransferResult(
            success=False,
            provider_name=self.provider_name,
            provider_reference=provider_reference,
            status="NOT_FOUND",
            amount=0.0,
            fee_charged=0.0,
            currency="FCFA",
            message=f"Transaction simulée {provider_reference} introuvable.",
            is_simulated=True
        )

