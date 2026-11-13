"""
Base interfaces and contracts for financial providers.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from packages.shared_schemas.mboa_schemas import PreparedTransaction


class ProviderTransferResult(BaseModel):
    """Normalized response from any financial provider execution."""
    success: bool
    provider_name: str
    provider_reference: str
    status: str
    amount: float
    fee_charged: float
    currency: str = "FCFA"
    message: str
    raw_response: Dict[str, Any] = Field(default_factory=dict)
    is_simulated: bool = False


class FinancialProviderBase(ABC):
    """Abstract base class for all payment/banking service integrations."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g., MTN_MOMO, ORANGE_MONEY, SIMULATED_BANK)."""
        pass

    @property
    @abstractmethod
    def is_simulation(self) -> bool:
        """Explicitly indicates whether this provider is simulated or executes real funds."""
        pass

    @abstractmethod
    async def get_balance(self, account_id: str) -> Optional[float]:
        """Queries authoritative balance for account, or returns None if unavailable."""
        pass

    @abstractmethod
    def quote_fee(self, amount: float) -> float:
        """Calculates precise provider fee based on official fee schedule."""
        pass

    @abstractmethod
    async def execute_transfer(
        self,
        transaction: PreparedTransaction,
        idempotency_key: str
    ) -> ProviderTransferResult:
        """Dispatches transfer to provider after all security authorizations pass."""
        pass

    @abstractmethod
    async def verify_transaction_status(self, provider_reference: str) -> ProviderTransferResult:
        """Queries status of an in-flight or completed transaction."""
        pass

