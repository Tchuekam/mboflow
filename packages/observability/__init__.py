"""
Observability Package for Mboa Finance AI.
Provides structured JSON logging, correlation ID tracing, and PII scrubbing.
"""

from .logger import setup_structured_logging, get_correlation_id, set_correlation_id, JSONLogFormatter

__all__ = [
    "setup_structured_logging",
    "get_correlation_id",
    "set_correlation_id",
    "JSONLogFormatter",
]

