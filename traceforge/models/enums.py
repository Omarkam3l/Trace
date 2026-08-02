"""Enumerations shared across TraceForge's data models."""

from __future__ import annotations

from enum import StrEnum


class SpanKind(StrEnum):
    """The role a span plays in the execution flow.

    Mirrors the vocabulary used by most tracing systems (OpenTelemetry
    included) so exporters can map onto it without surprises.
    """

    INTERNAL = "internal"
    CLIENT = "client"
    SERVER = "server"
    PRODUCER = "producer"
    CONSUMER = "consumer"


class SpanStatus(StrEnum):
    """The status of a span or trace."""

    UNSET = "unset"
    RUNNING = "running"
    OK = "ok"
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"


# Alias for Phase 1 specification
Status = SpanStatus


class EventLevel(StrEnum):
    """Severity of a structured event attached to a span."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
