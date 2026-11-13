"""
Adversarial Security and Financial Integrity Verification Suite for MboaFlow.
Tests:
1. SSRF prevention against private IP spaces, cloud metadata (169.254.169.254), and arbitrary local files.
2. Cryptographic HMAC parameter tampering detection at confirmation.
3. Enforced 120-second validity window and expiration handling.
4. Idempotency key replay protection and deduplication.
5. Ephemeral per-session BrowserContext isolation.
6. PII masking and redaction in audit trails and log strings.
7. End-to-end readiness probe verification.
"""

import os
import time
import pytest
from packages.shared_schemas.mboa_schemas import (
    TransactionStatus,
    VerificationStatus
)
from packages.security.action_guard import ActionGuard, SecurityViolationError
from packages.storage.repository import DatabaseRepository
from apps.browser_connector.connector import PlaywrightBrowserConnector
from packages.observability.logger import mask_sensitive_text


@pytest.fixture
def test_repo(tmp_path):
    db_file = str(tmp_path / "test_mboflow.db")
    return DatabaseRepository(db_path=db_file)


@pytest.fixture
def action_guard(test_repo):
    return ActionGuard(repository=test_repo, secret_key="test_adversarial_secret_key_123")


# ==============================================================================
# 1. SSRF and Navigation Boundary Tests
# ==============================================================================

def test_ssrf_blocks_cloud_metadata_ip():
    """Verify that cloud metadata IP 169.254.169.254 is strictly blocked."""
    connector = PlaywrightBrowserConnector(headless=True)
    with pytest.raises(SecurityViolationError) as exc_info:
        connector.validate_url("http://169.254.169.254/latest/meta-data/")
    assert "restricted range" in str(exc_info.value).lower()


def test_ssrf_blocks_private_rfc1918_ips():
    """Verify that RFC 1918 private subnets (10.x, 192.168.x, 172.16.x) and loopback are blocked."""
    connector = PlaywrightBrowserConnector(headless=True)

    dangerous_urls = [
        "http://127.0.0.1:8080/admin",
        "http://10.0.0.1/dashboard",
        "http://192.168.1.1/router",
        "http://172.16.0.5/api",
        "http://0.0.0.0/"
    ]
    for url in dangerous_urls:
        with pytest.raises(SecurityViolationError) as exc:
            connector.validate_url(url)
        assert "restricted range" in str(exc.value).lower() or "violation" in str(exc.value).lower()


def test_ssrf_blocks_arbitrary_local_files():
    """Verify that file:// URLs outside the simulated-bank directory are blocked."""
    connector = PlaywrightBrowserConnector(headless=True)

    # Windows / Unix sensitive paths
    with pytest.raises(SecurityViolationError):
        connector.validate_url("file:///etc/passwd")

    with pytest.raises(SecurityViolationError):
        connector.validate_url("file:///C:/Windows/System32/drivers/etc/hosts")


def test_safe_local_bank_file_is_permitted():
    """Verify that file:// pointing strictly inside simulated-bank is allowed for local test harnesses."""
    connector = PlaywrightBrowserConnector(headless=True)
    sim_bank_file = os.path.realpath(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "simulated-bank", "index.html"))
    )
    url = f"file:///{sim_bank_file.replace(os.sep, '/')}"
    # Should not raise exception
    connector.validate_url(url)


# ==============================================================================
# 2. Cryptographic Parameter Tampering & Expiration Tests
# ==============================================================================

def test_cryptographic_tamper_detection(action_guard):
    """
    Simulates an attacker altering the transfer amount or beneficiary
    between the preparation phase and the confirmation phase.
    """
    tx = action_guard.prepare_transaction(
        source_account="CM2110005001",
        beneficiary_name="Alice",
        beneficiary_account="699001122",
        amount=10000.0,
        fee=100.0,
        total_debit=10100.0,
        currency="FCFA"
    )

    # Tamper with the transaction amount in storage / cache
    tx.amount = 50000.0
    tx.total_debit = 50100.0
    action_guard.repository.save_transaction(tx)

    # Attempt confirmation
    with pytest.raises(SecurityViolationError) as exc:
        action_guard.confirm_transaction(
            transaction_id=tx.transaction_id,
            explicit_user_consent=True
        )
    assert "tampered" in str(exc.value).lower() or "breach" in str(exc.value).lower()


def test_transaction_expiration_rejected(action_guard):
    """
    Verifies that confirmation is rejected if the 120-second validity window expires.
    """
    tx = action_guard.prepare_transaction(
        source_account="CM2110005001",
        beneficiary_name="Bob",
        beneficiary_account="677002233",
        amount=5000.0,
        fee=100.0,
        total_debit=5100.0,
        currency="FCFA"
    )

    # Wind forward expiry to past
    tx.expires_at = time.time() - 5.0
    action_guard.repository.save_transaction(tx)

    with pytest.raises(SecurityViolationError) as exc:
        action_guard.confirm_transaction(
            transaction_id=tx.transaction_id,
            explicit_user_consent=True
        )
    assert "expired" in str(exc.value).lower()


# ==============================================================================
# 3. Idempotency & Replay Defense Tests
# ==============================================================================

def test_idempotency_prevents_duplicate_preparation(action_guard):
    """Submitting the exact same idempotency key returns the existing transaction."""
    key = "IDEMP-REQ-TEST-001"

    tx1 = action_guard.prepare_transaction(
        source_account="CM2110005001",
        beneficiary_name="Charlie",
        beneficiary_account="699334455",
        amount=15000.0,
        fee=100.0,
        total_debit=15100.0,
        currency="FCFA",
        idempotency_key=key
    )

    tx2 = action_guard.prepare_transaction(
        source_account="CM2110005001",
        beneficiary_name="Charlie",
        beneficiary_account="699334455",
        amount=15000.0,
        fee=100.0,
        total_debit=15100.0,
        currency="FCFA",
        idempotency_key=key
    )

    assert tx1.transaction_id == tx2.transaction_id
    assert tx1.signature == tx2.signature


def test_idempotency_prevents_duplicate_confirmation(action_guard):
    """Replaying confirmation with the same idempotency key does not re-execute."""
    prep_key = "IDEMP-PREP-002"
    conf_key = "IDEMP-CONF-002"

    tx = action_guard.prepare_transaction(
        source_account="CM2110005001",
        beneficiary_name="David",
        beneficiary_account="699112233",
        amount=20000.0,
        fee=100.0,
        total_debit=20100.0,
        currency="FCFA",
        idempotency_key=prep_key
    )

    # Confirm once
    confirmed_1 = action_guard.confirm_transaction(
        transaction_id=tx.transaction_id,
        explicit_user_consent=True,
        idempotency_key=conf_key
    )
    assert confirmed_1.status == TransactionStatus.CONFIRMED

    # Replay confirmation with identical key
    confirmed_2 = action_guard.confirm_transaction(
        transaction_id=tx.transaction_id,
        explicit_user_consent=True,
        idempotency_key=conf_key
    )
    assert confirmed_2.status == TransactionStatus.CONFIRMED
    assert confirmed_1.transaction_id == confirmed_2.transaction_id


# ==============================================================================
# 4. Ephemeral Browser Isolation & Session Cleanup Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_ephemeral_browser_context_isolation():
    """Verify that multiple sessions create isolated contexts without bleeding cookies/storage."""
    connector = PlaywrightBrowserConnector(headless=True)
    await connector.start()

    try:
        page_a = await connector.get_or_create_session_page("session_user_alice")
        page_b = await connector.get_or_create_session_page("session_user_bob")

        assert page_a != page_b
        assert page_a.context != page_b.context

        # Close Alice session
        await connector.close_session("session_user_alice")
        assert "session_user_alice" not in connector._session_contexts
        # Bob remains intact
        assert "session_user_bob" in connector._session_contexts
        await connector.close_session("session_user_bob")
    finally:
        await connector.stop()


# ==============================================================================
# 5. PII Masking & Redaction in Logs and Audit Trails
# ==============================================================================

def test_pii_scrubbing_phone_and_accounts():
    """Verify that phone numbers and account identifiers are scrubbed."""
    raw_log = "Transfer 50000 FCFA to recipient 699001122 from account CM2110005001234567890123"
    masked = mask_sensitive_text(raw_log)

    assert "699001122" not in masked
    assert "699***122" in masked
    assert "CM2110005001234567890123" not in masked
    assert "CM2110...0123" in masked


def test_action_guard_masks_audit_payload(action_guard):
    """Verify that audit logs persist masked payloads without plain phone numbers."""
    tx = action_guard.prepare_transaction(
        source_account="CM21100050012345",
        beneficiary_name="Paul Biya",
        beneficiary_account="677889900",
        amount=12000.0,
        fee=100.0,
        total_debit=12100.0,
        currency="FCFA"
    )

    trail = action_guard.get_audit_trail()
    assert len(trail) > 0

    latest_event = trail[0]
    payload = latest_event["payload"]

    # Beneficiary account masked
    assert "677889900" not in str(payload.get("beneficiary_account"))
    assert "677***900" in str(payload.get("beneficiary_account"))

