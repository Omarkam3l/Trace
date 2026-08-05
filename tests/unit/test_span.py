"""Unit tests for traceforge.core.span.Span."""

from __future__ import annotations

import pytest

from traceforge.api.exceptions import SpanNotActiveError
from traceforge.core.clock import FrozenClock
from traceforge.core.ids import generate_span_id, generate_trace_id
from traceforge.core.span import Span
from traceforge.models.enums import EventLevel, SpanKind, SpanStatus
from traceforge.models.span import SpanModel


def make_span(clock: FrozenClock) -> Span:
    model = SpanModel(
        id=generate_span_id(),
        trace_id=generate_trace_id(),
        parent_span_id=None,
        name="unit-span",
        kind=SpanKind.INTERNAL,
        status=SpanStatus.UNSET,
        start_time=clock.now(),
    )
    return Span(model, clock, clock.monotonic())


def test_span_starts_unfinished(frozen_clock):
    span = make_span(frozen_clock)
    assert not span.is_finished
    assert span.status is SpanStatus.UNSET


def test_finish_computes_duration(frozen_clock):
    span = make_span(frozen_clock)
    frozen_clock.advance(1.5)
    finished = span.finish()
    assert finished.duration_ms == pytest.approx(1500.0)
    assert finished.end_time is not None
    assert span.is_finished


def test_finish_is_idempotent(frozen_clock):
    span = make_span(frozen_clock)
    frozen_clock.advance(1.0)
    first = span.finish()
    frozen_clock.advance(10.0)
    second = span.finish()
    assert first == second


def test_set_attribute(frozen_clock):
    span = make_span(frozen_clock)
    span.set_attribute("k", "v")
    assert span.snapshot().attributes == {"k": "v"}


def test_set_attributes_merges(frozen_clock):
    span = make_span(frozen_clock)
    span.set_attribute("a", 1)
    span.set_attributes({"b": 2, "c": 3})
    assert span.snapshot().attributes == {"a": 1, "b": 2, "c": 3}


def test_add_event(frozen_clock):
    span = make_span(frozen_clock)
    span.add_event("cache-miss", attributes={"key": "x"}, level=EventLevel.WARNING)
    events = span.snapshot().events
    assert len(events) == 1
    assert events[0].name == "cache-miss"
    assert events[0].level is EventLevel.WARNING
    assert events[0].attributes == {"key": "x"}


def test_record_exception_sets_exception_and_adds_event(frozen_clock):
    span = make_span(frozen_clock)
    try:
        raise ValueError("boom")
    except ValueError as exc:
        span.record_exception(exc)

    snap = span.snapshot()
    assert snap.exception is not None
    assert snap.exception.type == "ValueError"
    assert snap.exception.message == "boom"
    assert any(e.name == "exception" for e in snap.events)


def test_set_status(frozen_clock):
    span = make_span(frozen_clock)
    span.set_status(SpanStatus.ERROR)
    assert span.snapshot().status is SpanStatus.ERROR


def test_mutating_finished_span_raises(frozen_clock):
    span = make_span(frozen_clock)
    span.finish()
    with pytest.raises(SpanNotActiveError):
        span.set_attribute("a", 1)
    with pytest.raises(SpanNotActiveError):
        span.add_event("x")
    with pytest.raises(SpanNotActiveError):
        span.set_status(SpanStatus.OK)


def test_concurrent_attribute_writes_are_thread_safe(frozen_clock):
    import threading

    span = make_span(frozen_clock)

    def writer(n: int):
        for i in range(50):
            span.set_attribute(f"k{n}", i)

    threads = [threading.Thread(target=writer, args=(n,)) for n in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    attrs = span.snapshot().attributes
    assert len(attrs) == 8  # one key per thread, no corrupted/lost writes


def test_live_span_attributes_property(frozen_clock):
    span = make_span(frozen_clock)
    assert span.attributes == {}
    span.set_attribute("env", "prod")
    assert span.attributes == {"env": "prod"}
    span.set_attributes({"tier": "api", "v": 1})
    assert span.attributes == {"env": "prod", "tier": "api", "v": 1}

