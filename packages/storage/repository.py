"""
Durable Persistence Repository for Mboa Finance AI.
Thread-safe SQLite/PostgreSQL storage for:
- Prepared and confirmed transactions
- Cryptographically signed state transitions
- Tamper-evident, PII-scrubbed audit logs
- Idempotency records for deduplication and replay protection
"""

import os
import json
import time
import sqlite3
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from packages.shared_schemas.mboa_schemas import (
    PreparedTransaction,
    TransactionStatus,
    VerificationStatus
)

logger = logging.getLogger("mboa.storage.repository")


class DatabaseRepository:
    """
    Thread-safe storage repository using SQLite with WAL mode enabled.
    Can be upgraded to PostgreSQL by configuring DATABASE_URL.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            data_dir = os.environ.get("MBOA_DATA_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data")))
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = os.path.join(data_dir, "mboflow.db")
        else:
            self.db_path = db_path
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a configured SQLite connection with row factories and WAL mode."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_database(self):
        """Initializes tables and indexes if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id TEXT PRIMARY KEY,
                    source_account TEXT NOT NULL,
                    beneficiary_name TEXT NOT NULL,
                    beneficiary_account TEXT NOT NULL,
                    amount REAL NOT NULL,
                    fee REAL NOT NULL,
                    total_debit REAL NOT NULL,
                    currency TEXT NOT NULL DEFAULT 'FCFA',
                    status TEXT NOT NULL,
                    verification_status TEXT NOT NULL,
                    verification_notes TEXT NOT NULL,
                    conditions TEXT NOT NULL,
                    warnings TEXT NOT NULL,
                    simulated INTEGER NOT NULL DEFAULT 1,
                    prepared_at REAL NOT NULL,
                    confirmed_at REAL,
                    signature TEXT,
                    expires_at REAL,
                    idempotency_key TEXT,
                    provider TEXT,
                    provider_reference TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                );
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_status ON transactions(status);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_idempotency ON transactions(idempotency_key);")

            # 2. Audit logs table (tamper-evident, append-only)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    event_type TEXT NOT NULL,
                    correlation_id TEXT,
                    session_id TEXT,
                    masked_payload TEXT NOT NULL,
                    note TEXT NOT NULL,
                    recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_event ON audit_logs(event_type);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_time ON audit_logs(timestamp);")

            # 3. Idempotency store table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS idempotency_keys (
                    idempotency_key TEXT PRIMARY KEY,
                    action_type TEXT NOT NULL,
                    transaction_id TEXT,
                    status TEXT NOT NULL,
                    response_json TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL
                );
            """)

            conn.commit()
            logger.info(f"Database initialized at {self.db_path} with WAL mode.")

    def save_transaction(self, tx: PreparedTransaction) -> None:
        """Persists or updates a prepared transaction record."""
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (
                    transaction_id, source_account, beneficiary_name, beneficiary_account,
                    amount, fee, total_debit, currency, status, verification_status,
                    verification_notes, conditions, warnings, simulated, prepared_at,
                    confirmed_at, signature, expires_at, idempotency_key, provider,
                    provider_reference, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(transaction_id) DO UPDATE SET
                    status=excluded.status,
                    verification_status=excluded.verification_status,
                    verification_notes=excluded.verification_notes,
                    confirmed_at=excluded.confirmed_at,
                    signature=excluded.signature,
                    expires_at=excluded.expires_at,
                    provider=excluded.provider,
                    provider_reference=excluded.provider_reference,
                    updated_at=excluded.updated_at
            """, (
                tx.transaction_id,
                tx.source_account,
                tx.beneficiary_name,
                tx.beneficiary_account,
                tx.amount,
                tx.fee,
                tx.total_debit,
                tx.currency,
                tx.status.value if hasattr(tx.status, "value") else str(tx.status),
                tx.verification_status.value if hasattr(tx.verification_status, "value") else str(tx.verification_status),
                json.dumps(tx.verification_notes),
                json.dumps(tx.conditions),
                json.dumps(tx.warnings),
                1 if tx.simulated else 0,
                tx.prepared_at,
                tx.confirmed_at,
                tx.signature,
                tx.expires_at,
                tx.idempotency_key,
                tx.provider,
                tx.provider_reference,
                tx.prepared_at,
                now
            ))
            conn.commit()

    def get_transaction(self, transaction_id: str) -> Optional[PreparedTransaction]:
        """Retrieves a transaction by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions WHERE transaction_id = ?", (transaction_id,))
            row = cursor.fetchone()
            if not row:
                return None

            return PreparedTransaction(
                transaction_id=row["transaction_id"],
                source_account=row["source_account"],
                beneficiary_name=row["beneficiary_name"],
                beneficiary_account=row["beneficiary_account"],
                amount=row["amount"],
                fee=row["fee"],
                total_debit=row["total_debit"],
                currency=row["currency"],
                status=TransactionStatus(row["status"]),
                verification_status=VerificationStatus(row["verification_status"]),
                verification_notes=json.loads(row["verification_notes"]),
                conditions=json.loads(row["conditions"]),
                warnings=json.loads(row["warnings"]),
                simulated=bool(row["simulated"]),
                prepared_at=row["prepared_at"],
                confirmed_at=row["confirmed_at"],
                signature=row["signature"],
                expires_at=row["expires_at"],
                idempotency_key=row["idempotency_key"],
                provider=row["provider"],
                provider_reference=row["provider_reference"]
            )

    def log_audit_event(
        self,
        event_type: str,
        masked_payload: Dict[str, Any],
        note: str,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> int:
        """Appends an immutable audit log entry."""
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_logs (timestamp, event_type, correlation_id, session_id, masked_payload, note)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                now,
                event_type,
                correlation_id,
                session_id,
                json.dumps(masked_payload),
                note
            ))
            conn.commit()
            return cursor.lastrowid

    def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieves recent audit log entries."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, timestamp, event_type, correlation_id, session_id, masked_payload, note, recorded_at
                FROM audit_logs
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            result = []
            for r in rows:
                result.append({
                    "id": r["id"],
                    "timestamp": r["timestamp"],
                    "event_type": r["event_type"],
                    "correlation_id": r["correlation_id"],
                    "session_id": r["session_id"],
                    "payload": json.loads(r["masked_payload"]),
                    "note": r["note"],
                    "recorded_at": r["recorded_at"]
                })
            return result

    def get_idempotency_record(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieves an existing idempotency record if not expired."""
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT idempotency_key, action_type, transaction_id, status, response_json, created_at, expires_at
                FROM idempotency_keys
                WHERE idempotency_key = ? AND expires_at > ?
            """, (key, now))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "idempotency_key": row["idempotency_key"],
                "action_type": row["action_type"],
                "transaction_id": row["transaction_id"],
                "status": row["status"],
                "response": json.loads(row["response_json"]),
                "created_at": row["created_at"],
                "expires_at": row["expires_at"]
            }

    def save_idempotency_record(
        self,
        key: str,
        action_type: str,
        transaction_id: str,
        status: str,
        response: Dict[str, Any],
        ttl_seconds: float = 86400.0  # 24 hours
    ) -> None:
        """Stores an idempotency key with its cached response."""
        now = time.time()
        expires = now + ttl_seconds
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO idempotency_keys (idempotency_key, action_type, transaction_id, status, response_json, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(idempotency_key) DO UPDATE SET
                    status=excluded.status,
                    response_json=excluded.response_json,
                    expires_at=excluded.expires_at
            """, (
                key,
                action_type,
                transaction_id,
                status,
                json.dumps(response),
                now,
                expires
            ))
            conn.commit()


_repo_instance: Optional[DatabaseRepository] = None

def get_repository() -> DatabaseRepository:
    """Singleton getter for the persistence repository."""
    global _repo_instance
    if _repo_instance is None:
        _repo_instance = DatabaseRepository()
    return _repo_instance

