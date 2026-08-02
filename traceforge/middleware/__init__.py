"""Generic, framework-agnostic middleware primitives.

These are building blocks for future framework-specific instrumentation
(see ``traceforge.instrumentation``) — not middleware for any particular
framework themselves.
"""

from traceforge.middleware.correlation import (
    CORRELATION_ID_HEADER,
    extract_correlation_id,
    inject_correlation_id,
)
from traceforge.middleware.request import RequestContext
from traceforge.middleware.response import ResponseContext
from traceforge.middleware.timing import timed_call, timed_call_async

__all__ = [
    "CORRELATION_ID_HEADER",
    "RequestContext",
    "ResponseContext",
    "extract_correlation_id",
    "inject_correlation_id",
    "timed_call",
    "timed_call_async",
]
