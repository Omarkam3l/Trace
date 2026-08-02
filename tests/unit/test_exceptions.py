"""Unit tests for traceforge.api.exceptions hierarchy."""

from __future__ import annotations

from traceforge.api.exceptions import (
    ConfigurationError,
    ExporterError,
    SpanNotActiveError,
    StorageError,
    TraceForgeError,
    TracerNotConfiguredError,
)


def test_all_exceptions_inherit_from_base():
    for exc_cls in (
        SpanNotActiveError,
        TracerNotConfiguredError,
        StorageError,
        ExporterError,
        ConfigurationError,
    ):
        assert issubclass(exc_cls, TraceForgeError)


def test_exceptions_carry_messages():
    err = StorageError("disk full")
    assert str(err) == "disk full"
