"""
Financial Provider Router for Mboa Finance AI.
Intelligently routes transactions to the authoritative provider based on recipient identifier format,
phone prefix, or configured banking connector.
"""

import re
import logging
from typing import Dict, Optional
from .base import FinancialProviderBase
from .simulated_provider import SimulatedBankingProvider
from .mtn_momo import MTNMoMoProvider
from .orange_money import OrangeMoneyProvider

logger = logging.getLogger("mboa.providers.router")


class FinancialProviderRouter:
    """
    Routes payments to MTN MoMo, Orange Money, or Banking providers based on account number / phone format.
    """

    MTN_PREFIXES = (
        "67", "68", "650", "651", "652", "653", "654"
    )
    ORANGE_PREFIXES = (
        "69", "655", "656", "657", "658", "659"
    )

    def __init__(
        self,
        simulated_provider: Optional[SimulatedBankingProvider] = None,
        mtn_provider: Optional[MTNMoMoProvider] = None,
        orange_provider: Optional[OrangeMoneyProvider] = None,
        force_simulation: bool = False
    ):
        self.simulated = simulated_provider or SimulatedBankingProvider()
        self.mtn = mtn_provider or MTNMoMoProvider()
        self.orange = orange_provider or OrangeMoneyProvider()
        self.force_simulation = force_simulation

    def resolve_provider(self, identifier: str) -> FinancialProviderBase:
        """
        Determines the correct provider from the beneficiary identifier.
        """
        if self.force_simulation:
            return self.simulated

        # Clean phone number (strip whitespace, +237, leading zeros)
        clean = re.sub(r'\D', '', identifier)
        if clean.startswith("237") and len(clean) == 12:
            clean = clean[3:]

        # Check MTN prefixes
        if any(clean.startswith(p) for p in self.MTN_PREFIXES):
            return self.mtn

        # Check Orange prefixes
        if any(clean.startswith(p) for p in self.ORANGE_PREFIXES):
            return self.orange

        # If it matches a bank IBAN or general account, or simulation mode is default
        return self.simulated

    def quote_fee(self, beneficiary_account: str, amount: float) -> float:
        """Quotes fee using the provider that matches the recipient destination."""
        provider = self.resolve_provider(beneficiary_account)
        return provider.quote_fee(amount)

