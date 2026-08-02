"""Framework-agnostic correlation-ID propagation helpers.

Works with any ``Mapping``/``MutableMapping`` of headers, so it can be
wired into any framework's request/response objects without TraceForge
needing to know about that framework.
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping

from traceforge.core.ids import generate_correlation_id

CORRELATION_ID_HEADER = "X-Correlation-ID"


def extract_correlation_id(headers: Mapping[str, str]) -> str | None:
    """Case-insensitively look up the correlation ID header, if present."""
    target = CORRELATION_ID_HEADER.lower()
    for key, value in headers.items():
        if key.lower() == target:
            return value
    return None


def inject_correlation_id(
    headers: MutableMapping[str, str], correlation_id: str | None = None
) -> str:
    """Set the correlation ID header, generating one if not provided.

    Returns the correlation ID that was set.
    """
    cid = correlation_id or generate_correlation_id()
    headers[CORRELATION_ID_HEADER] = cid
    return cid
