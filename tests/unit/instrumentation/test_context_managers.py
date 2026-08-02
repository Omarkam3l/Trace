"""Unit tests for sync and async session and activity context managers."""

from __future__ import annotations

import pytest

from traceforge.instrumentation.tracer import Tracer


def test_sync_session_and_activity_context_managers():
    tracer = Tracer()

    with tracer.session("Order Processing"):
        assert tracer.is_recording()

        with tracer.activity("Validate Inventory"):
            assert tracer.current_activity().name == "Validate Inventory"
            tracer.event("Stock available")

        with tracer.activity("Charge Card"):
            assert tracer.current_activity().name == "Charge Card"
            tracer.event("Payment authorized")

    assert not tracer.is_recording()


@pytest.mark.asyncio
async def test_async_session_and_activity_context_managers():
    tracer = Tracer()

    async with tracer.session("Async Order Processing"):
        assert tracer.is_recording()

        async with tracer.activity("Async Fetch Details"):
            assert tracer.current_activity().name == "Async Fetch Details"
            tracer.event("Details fetched")

    assert not tracer.is_recording()
