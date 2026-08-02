"""Unit tests for traceforge.core.tracer.Tracer."""

from __future__ import annotations

import asyncio

import pytest

from traceforge.core.context import ContextManager
from traceforge.core.lifecycle import SpanLifecycleHook
from traceforge.models.enums import SpanKind, SpanStatus
from traceforge.models.span import SpanModel


class RecordingHook(SpanLifecycleHook):
    def __init__(self):
        self.started: list[SpanModel] = []
        self.ended: list[SpanModel] = []

    def on_span_start(self, span: SpanModel) -> None:
        self.started.append(span)

    def on_span_end(self, span: SpanModel) -> None:
        self.ended.append(span)


def test_root_span_gets_new_trace_id(tracer):
    with tracer.start_span("root") as span:
        assert span.trace_id
        assert span.parent_span_id is None


def test_nested_span_shares_trace_id_and_has_parent(tracer):
    with tracer.start_span("outer") as outer:
        with tracer.start_span("inner") as inner:
            assert inner.trace_id == outer.trace_id
            assert inner.parent_span_id == outer.id


def test_sibling_spans_share_same_parent(tracer):
    with tracer.start_span("outer") as outer:
        with tracer.start_span("child-a") as a:
            pass
        with tracer.start_span("child-b") as b:
            pass
    assert a.parent_span_id == outer.id
    assert b.parent_span_id == outer.id


def test_context_restored_after_span_exits(tracer):
    assert ContextManager.get_current().span_id is None
    with tracer.start_span("root") as root:
        assert ContextManager.get_current().span_id == root.id
    assert ContextManager.get_current().span_id is None


def test_context_restored_after_exception(tracer):
    with pytest.raises(ValueError):
        with tracer.start_span("root"):
            raise ValueError("boom")
    assert ContextManager.get_current().is_empty()


def test_exception_marks_span_as_error_and_captures_it(tracer):
    hook = RecordingHook()
    tracer.add_hook(hook)
    with pytest.raises(ValueError):
        with tracer.start_span("failing"):
            raise ValueError("boom")

    ended = hook.ended[0]
    assert ended.status is SpanStatus.ERROR
    assert ended.exception is not None
    assert ended.exception.message == "boom"


def test_successful_span_defaults_to_ok_status(tracer):
    hook = RecordingHook()
    tracer.add_hook(hook)
    with tracer.start_span("ok-span"):
        pass
    assert hook.ended[0].status is SpanStatus.OK


def test_explicit_status_is_not_overridden(tracer):
    hook = RecordingHook()
    tracer.add_hook(hook)
    with tracer.start_span("custom-status") as span:
        span.set_status(SpanStatus.ERROR)
    assert hook.ended[0].status is SpanStatus.ERROR


def test_duration_is_computed(tracer, frozen_clock):
    hook = RecordingHook()
    tracer.add_hook(hook)
    with tracer.start_span("timed"):
        frozen_clock.advance(0.25)
    assert hook.ended[0].duration_ms == pytest.approx(250.0)


def test_hooks_receive_start_and_end_events(tracer):
    hook = RecordingHook()
    tracer.add_hook(hook)
    with tracer.start_span("s"):
        pass
    assert len(hook.started) == 1
    assert len(hook.ended) == 1
    assert hook.started[0].id == hook.ended[0].id


def test_remove_hook_stops_notifications(tracer):
    hook = RecordingHook()
    tracer.add_hook(hook)
    tracer.remove_hook(hook)
    with tracer.start_span("s"):
        pass
    assert hook.started == []
    assert hook.ended == []


def test_attributes_are_attached_at_span_start(tracer):
    hook = RecordingHook()
    tracer.add_hook(hook)
    with tracer.start_span("s", attributes={"a": 1}):
        pass
    assert hook.started[0].attributes == {"a": 1}


def test_span_kind_is_propagated(tracer):
    with tracer.start_span("client-call", kind=SpanKind.CLIENT) as span:
        assert span.snapshot().kind is SpanKind.CLIENT


async def test_async_span_context_manager(tracer):
    async with tracer.start_span("async-root") as root:
        await asyncio.sleep(0)
        async with tracer.start_span("async-child") as child:
            assert child.trace_id == root.trace_id
            assert child.parent_span_id == root.id


async def test_context_isolated_across_concurrent_tasks(tracer):
    trace_ids = {}

    async def worker(name: str):
        async with tracer.start_span(f"root-{name}") as root:
            await asyncio.sleep(0.01)
            trace_ids[name] = root.trace_id

    await asyncio.gather(worker("a"), worker("b"), worker("c"))
    assert len(set(trace_ids.values())) == 3  # each got its own trace


def test_correlation_id_propagates_to_children(tracer):
    with tracer.start_span("root") as root:
        with tracer.start_span("child") as child:
            assert child.snapshot().correlation_id == root.snapshot().correlation_id


def test_multiple_root_spans_get_different_trace_ids(tracer):
    with tracer.start_span("root-1") as r1:
        pass
    with tracer.start_span("root-2") as r2:
        pass
    assert r1.trace_id != r2.trace_id


def test_active_trace_count_reflects_open_spans(tracer):
    assert tracer.active_trace_count() == 0
    with tracer.start_span("root"):
        assert tracer.active_trace_count() == 1
        with tracer.start_span("child"):
            assert tracer.active_trace_count() == 1  # same trace
    assert tracer.active_trace_count() == 0


def test_deeply_nested_spans(tracer):
    depth = 25
    ids = []

    def recurse(n: int):
        if n == 0:
            return
        with tracer.start_span(f"level-{n}") as span:
            ids.append(span.id)
            recurse(n - 1)

    recurse(depth)
    assert len(ids) == depth
    assert len(set(ids)) == depth  # all unique
