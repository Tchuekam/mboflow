"""
Production Structured JSON Logging with PII Scrubbing and Correlation ID tracing.
"""

import re
import json
import time
import logging
import contextvars
from typing import Optional, Any, Dict

correlation_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("correlation_id", default=None)
session_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("session_id", default=None)

PHONE_PATTERN = re.compile(r'\b(?:\+?237\s*)?(6[25789]\d{7}|2[234]\d{7})\b')
ACCOUNT_PATTERN = re.compile(r'\b(CM\d{2}[A-Z0-9]{16,24}|[0-9]{11,20})\b')


def get_correlation_id() -> Optional[str]:
    return correlation_id_var.get()


def set_correlation_id(cid: str) -> None:
    correlation_id_var.set(cid)


def get_session_id() -> Optional[str]:
    return session_id_var.get()


def set_session_id(sid: str) -> None:
    session_id_var.set(sid)


def mask_sensitive_text(text: str) -> str:
    """Masks phone numbers and bank account numbers in log strings."""
    if not isinstance(text, str):
        return text

    # Mask phones: e.g. 699001122 -> 699***122
    def _mask_phone(m):
        raw = m.group(0).strip()
        if len(raw) >= 9:
            return raw[:3] + "***" + raw[-3:]
        return "***"

    # Mask accounts: e.g. CM2110005001234567890123 -> CM2110...0123
    def _mask_account(m):
        raw = m.group(0).strip()
        if len(raw) >= 12:
            return raw[:6] + "..." + raw[-4:]
        return "..."

    masked = PHONE_PATTERN.sub(_mask_phone, text)
    masked = ACCOUNT_PATTERN.sub(_mask_account, masked)
    return masked


class JSONLogFormatter(logging.Formatter):
    """Formats log records as structured single-line JSON."""

    def __init__(self, service_name: str = "mboa-backend"):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "service": self.service_name,
            "logger": record.name,
            "message": mask_sensitive_text(record.getMessage()),
            "correlation_id": get_correlation_id() or getattr(record, "correlation_id", None),
            "session_id": get_session_id() or getattr(record, "session_id", None),
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


def setup_structured_logging(service_name: str = "mboa-backend", level: int = logging.INFO):
    """Configures root logger with structured JSON handler."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler()
    handler.setFormatter(JSONLogFormatter(service_name=service_name))
    root_logger.addHandler(handler)

    # Silence verbose 3rd party logs
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

