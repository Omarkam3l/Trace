"""Unit tests validating Phase 1 Core SDK Foundation requirements and acceptance criteria."""

from __future__ import annotations

import concurrent.futures

import pytest

from traceforge.core.tracer import Tracer
from traceforge.exceptions import SpanNotActiveError, TraceForgeError
from traceforge.models.enums import SpanStatus, Status
from traceforge.storage.memory import MemoryStorage


def test_acceptance_criteria_exact_snippet():
    """Validates the exact code snippet given in Phase 1 Acceptance Criteria."""
    tracer = Tracer("login-service")

    trace = tracer.start_trace("Login")
    span = trace.start_span("Database")
    span.add_event("SELECT user")
    span.finish()
    completed_trace = trace.finish()

    assert completed_trace is not None
    assert completed_trace.name == "Login"
    assert completed_trace.id is not None
    assert completed_trace.root_span is not None
    assert completed_trace.root_span.name == "Login"
    assert len(completed_trace.spans) == 2
    assert completed_trace.duration_ms is not None
    assert completed_trace.duration_ms >= 0.0

    # Verify event on child span
    db_span = next(s for s in completed_trace.spans if s.name == "Database")
    assert db_span.parent_id == completed_trace.root_span.id
    assert len(db_span.events) == 1
    assert db_span.events[0].name == "SELECT user"
    assert db_span.events[0].span_id == db_span.id


def test_trace_lifecycle_and_duration(frozen_clock):
    tracer = Tracer("checkout-service", clock=frozen_clock)

    trace = tracer.start_trace("Checkout")
    frozen_clock.advance(0.10)  # 100ms

    span1 = trace.start_span("Validate User")
    frozen_clock.advance(0.05)  # 50ms
    span1.add_event("User Found", attributes={"user.id": "42"})
    span1.finish()

    span2 = trace.start_span("Payment")
    frozen_clock.advance(0.15)  # 150ms
    span2.finish()

    completed = trace.finish()

    assert completed.duration_ms == pytest.approx(300.0)
    assert completed.status == SpanStatus.SUCCESS
    assert completed.root_span.children is not None
    assert len(completed.root_span.children) == 2


def test_nested_spans_tree_hierarchy(frozen_clock):
    tracer = Tracer("order-service", clock=frozen_clock)

    trace = tracer.start_trace("Checkout")
    
    with trace.start_span("Payment") as payment:
        payment.add_event("Processing Payment")
        with payment.start_span("Stripe Request") as stripe_req:
            frozen_clock.advance(0.05)
            stripe_req.add_event("Payload Sent")
        with payment.start_span("Stripe Response") as stripe_resp:
            frozen_clock.advance(0.05)
            stripe_resp.add_event("Success Response")

    completed = trace.finish()

    root = completed.root_span
    assert root is not None
    assert root.name == "Checkout"
    assert len(root.children) == 1

    payment_node = root.children[0]
    assert payment_node.name == "Payment"
    assert len(payment_node.children) == 2

    child_names = {c.name for c in payment_node.children}
    assert child_names == {"Stripe Request", "Stripe Response"}


def test_status_transitions_and_aliases():
    tracer = Tracer("status-service")

    # Success status
    trace_ok = tracer.start_trace("OK Trace")
    span_ok = trace_ok.start_span("Task")
    span_ok.set_status(Status.OK)
    span_ok.finish()
    res_ok = trace_ok.finish(Status.SUCCESS)
    assert res_ok.status == Status.SUCCESS

    # Cancelled status
    trace_cancelled = tracer.start_trace("Cancelled Trace")
    span_c = trace_cancelled.start_span("Task")
    span_c.set_status(Status.CANCELLED)
    span_c.finish()
    res_c = trace_cancelled.finish(Status.CANCELLED)
    assert res_c.status == Status.CANCELLED

    # Error status
    trace_err = tracer.start_trace("Error Trace")
    span_e = trace_err.start_span("Task")
    span_e.set_status(Status.ERROR)
    span_e.finish()
    res_err = trace_err.finish(Status.ERROR)
    assert res_err.status == Status.ERROR


def test_exception_handling_in_spans(tracer):
    trace = tracer.start_trace("Exception Trace")
    span = trace.start_span("Failing Step")

    try:
        raise ValueError("Database connection failed")
    except ValueError as exc:
        span.record_exception(exc)
        span.set_status(SpanStatus.ERROR)
        span.finish()

    completed = trace.finish(status=SpanStatus.ERROR)
    assert completed.status == SpanStatus.ERROR

    failing_span = next(s for s in completed.spans if s.name == "Failing Step")
    assert failing_span.status == SpanStatus.ERROR
    assert failing_span.exception is not None
    assert failing_span.exception.type == "ValueError"
    assert failing_span.exception.message == "Database connection failed"


def test_mutating_finished_span_raises():
    tracer = Tracer("test")
    trace = tracer.start_trace("t")
    span = trace.start_span("s")
    span.finish()

    with pytest.raises(SpanNotActiveError):
        span.add_event("too late")

    with pytest.raises(TraceForgeError):
        span.set_attribute("k", "v")


def test_concurrent_trace_creation():
    tracer = Tracer("concurrent-service")

    def run_trace(index: int):
        trace = tracer.start_trace(f"Trace-{index}")
        for j in range(3):
            span = trace.start_span(f"Span-{index}-{j}")
            span.add_event(f"Event-{index}-{j}")
            span.finish()
        return trace.finish()

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(run_trace, i) for i in range(10)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert len(results) == 10
    trace_ids = {r.id for r in results}
    assert len(trace_ids) == 10


@pytest.mark.asyncio
async def test_in_memory_storage_query():
    storage = MemoryStorage(max_spans=100)
    tracer = Tracer("mem-test")

    trace = tracer.start_trace("In-Memory Trace")
    span = trace.start_span("Work")
    span.finish()
    completed = trace.finish()

    await storage.write_spans(completed.spans)
    query_res = await storage.query_spans(trace_id=completed.id)

    assert len(query_res) == 2
    assert len(storage) == 2
    await storage.close()
