"""Unit tests verifying safe failure guarantees (application exceptions propagate normally while recording cleans up safely)."""

from __future__ import annotations

import pytest

from traceforge.instrumentation.tracer import Tracer


def test_exception_in_decorated_function_propagates_and_cleans_up():
    tracer = Tracer()

    @tracer
    def failing_function():
        raise ValueError("App error in business logic")

    with tracer.session("Error Test") as sess_cm:
        with pytest.raises(ValueError) as exc_info:
            failing_function()
        assert "App error in business logic" in str(exc_info.value)

    # Verify session stops cleanly despite the exception in decorated function
    session = sess_cm.completed_session
    assert not tracer.is_recording()
    assert len(session.activities) >= 1


def test_exception_in_context_manager_propagates_and_cleans_up():
    tracer = Tracer()

    with pytest.raises(ZeroDivisionError):
        with tracer.session("Failing Session"):
            with tracer.activity("Failing Activity"):
                _ = 1 / 0

    assert not tracer.is_recording()
