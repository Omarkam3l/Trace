"""Bridges between traceforge's public SDK pipeline and its internal domain-object

execution pipeline.
"""

from __future__ import annotations

from traceforge.bridge.span_to_session import SpanToSessionBridge

__all__ = ["SpanToSessionBridge"]
