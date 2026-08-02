"""Storage exception hierarchy for Phase 6.2 Buffer Manager & Flush Engine."""

from __future__ import annotations

from traceforge.api.exceptions import TraceForgeError


class BufferOverflowError(TraceForgeError):
    """Raised when appending to BufferManager exceeds max_capacity limit."""


class FlushError(TraceForgeError):
    """Raised when an error occurs during buffer flush or batch write execution."""


class TransactionError(TraceForgeError):
    """Raised when transaction management operations fail or invalid nested transactions occur."""
