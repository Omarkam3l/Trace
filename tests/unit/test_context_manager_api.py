"""Unit tests for traceforge.api.context_manager and functions."""

from __future__ import annotations

import pytest

import traceforge
from traceforge.api.exceptions import TracerNotConfiguredError


def test_span_requires_configured_tracer():
    with pytest.raises(TracerNotConfiguredError):
        with traceforge.span("x"):
            pass


def test_span_uses_configured_default_tracer(tracer):
    traceforge.configure(tracer)
    with traceforge.span("root") as s:
        assert s.name == "root"
    assert traceforge.current_span_id() is None  # restored after exit


def test_set_correlation_id_binds_to_context(tracer):
    traceforge.configure(tracer)
    token = traceforge.set_correlation_id("my-correlation")
    try:
        assert traceforge.current_correlation_id() == "my-correlation"
    finally:
        from traceforge.core.context import ContextManager

        ContextManager.reset(token)


def test_new_session_binds_session_id(tracer):
    token = traceforge.new_session("session-123")
    try:
        assert traceforge.current_session_id() == "session-123"
    finally:
        from traceforge.core.context import ContextManager

        ContextManager.reset(token)


def test_is_configured_reflects_state(tracer):
    assert traceforge.is_configured() is False
    traceforge.configure(tracer)
    assert traceforge.is_configured() is True
    traceforge.reset_default_tracer()
    assert traceforge.is_configured() is False
