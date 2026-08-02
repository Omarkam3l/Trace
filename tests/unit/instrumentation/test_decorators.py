"""Unit tests for function decorators (@trace, @trace.activity, @trace.session)."""

from __future__ import annotations

import pytest

from traceforge.instrumentation.tracer import Tracer


def test_sync_function_decorators():
    tracer = Tracer()

    @tracer
    def process_data(x: int) -> int:
        assert tracer.current_activity().name == "process_data"
        tracer.event("Data processed")
        return x * 2

    @tracer("custom_step")
    def step_two():
        assert tracer.current_activity().name == "custom_step"

    with tracer.session("Decorator Test") as sess_cm:
        res = process_data(21)
        assert res == 42
        step_two()

    session = sess_cm.completed_session
    # 3 activities: default activity, process_data activity, custom_step activity
    activity_names = [a.name for a in session.activities]
    assert "process_data" in activity_names
    assert "custom_step" in activity_names


@pytest.mark.asyncio
async def test_async_function_decorators():
    tracer = Tracer()

    @tracer
    async def async_fetch():
        assert tracer.current_activity().name == "async_fetch"
        tracer.event("Async fetched")
        return "ok"

    async with tracer.session("Async Decorator Test") as sess_cm:
        res = await async_fetch()
        assert res == "ok"

    session = sess_cm.completed_session
    activity_names = [a.name for a in session.activities]
    assert "async_fetch" in activity_names
