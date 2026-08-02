"""Identifier generation for traces, spans, correlation and sessions.

Centralized here so the ID format (currently UUID4-derived hex) can change
in one place without rippling through the rest of the SDK.
"""

from __future__ import annotations

import uuid


def generate_trace_id() -> str:
    """A 32-hex-character globally unique trace identifier."""
    return uuid.uuid4().hex


def generate_span_id() -> str:
    """A 16-hex-character globally unique span identifier."""
    return uuid.uuid4().hex[:16]


def generate_correlation_id() -> str:
    """An identifier for correlating events across service/process boundaries."""
    return uuid.uuid4().hex


def generate_session_id() -> str:
    """An identifier for grouping traces that belong to one user/runtime session."""
    return uuid.uuid4().hex


def generate_event_id() -> str:
    return uuid.uuid4().hex[:16]
