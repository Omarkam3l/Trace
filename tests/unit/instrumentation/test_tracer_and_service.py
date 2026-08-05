"""Unit tests for Tracer facade and InstrumentationService."""

from __future__ import annotations

from traceforge.instrumentation.tracer import Tracer


def test_tracer_session_activity_and_events():
    tracer = Tracer()

    session = tracer.start_session(name="API Session")
    assert tracer.is_recording()
    assert tracer.current_session()["session_id"] == session.id

    tracer.start_activity("Database Query")
    assert tracer.current_activity().name == "Database Query"

    tracer.event("Cache hit", metadata={"key": "user_123"})
    tracer.event("Cache miss", payload={"key": "order_456"})

    completed_activity = tracer.stop_activity()
    assert completed_activity.name == "Database Query"
    assert len(completed_activity.graph.nodes) == 2

    completed_session = tracer.stop_session()
    assert not tracer.is_recording()
    assert len(completed_session.activities) >= 1
