"""Pydantic data models for TraceForge.

These are pure, framework-agnostic serialization schemas. They carry no
behavior beyond validation — behavior (starting/ending spans, computing
durations, etc.) lives in ``traceforge.core``.
"""

from traceforge.models.enums import EventLevel, SpanKind, SpanStatus
from traceforge.models.event import EventModel
from traceforge.models.metadata import Attributes, ExceptionInfo, sanitize_attributes
from traceforge.models.span import SpanModel
from traceforge.models.trace import TraceModel

__all__ = [
    "Attributes",
    "EventLevel",
    "EventModel",
    "ExceptionInfo",
    "SpanKind",
    "SpanModel",
    "SpanStatus",
    "TraceModel",
    "sanitize_attributes",
]
