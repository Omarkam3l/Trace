"""Unit tests for traceforge.recorder.Recorder."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from traceforge.models.enums import SpanKind, SpanStatus
from traceforge.models.span import SpanModel
from traceforge.recorder.recorder import Recorder
from traceforge.storage.memory import MemoryStorage


def make_span(**overrides) -> SpanModel:
    defaults = dict(
        id="s1",
        trace_id="t1",
        name="x",
        kind=SpanKind.INTERNAL,
        status=SpanStatus.OK,
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        duration_ms=1.0,
    )
    defaults.update(overrides)
    return SpanModel(**defaults)


async def _wait_until(predicate, timeout=2.0, interval=0.02):
    elapsed = 0.0
    while elapsed < timeout:
        if predicate():
            return True
        await asyncio.sleep(interval)
        elapsed += interval
    return False


async def test_recorded_spans_reach_storage():
    storage = MemoryStorage()
    recorder = Recorder(storage=storage, batch_size=2, flush_interval=0.1).start()
    try:
        recorder.on_span_end(make_span(id="a"))
        recorder.on_span_end(make_span(id="b"))
        recorder.on_span_end(make_span(id="c"))

        ok = await _wait_until(lambda: len(storage) == 3)
        assert ok, f"expected 3 spans, got {len(storage)}"
    finally:
        recorder.stop()


async def test_flush_interval_flushes_partial_batches():
    storage = MemoryStorage()
    recorder = Recorder(storage=storage, batch_size=100, flush_interval=0.1).start()
    try:
        recorder.on_span_end(make_span(id="only-one"))
        ok = await _wait_until(lambda: len(storage) == 1)
        assert ok
    finally:
        recorder.stop()


async def test_stop_flushes_remaining_spans():
    storage = MemoryStorage()
    recorder = Recorder(storage=storage, batch_size=1000, flush_interval=1000).start()
    for i in range(5):
        recorder.on_span_end(make_span(id=str(i)))
    recorder.stop(timeout=5)
    assert len(storage) == 5


async def test_exporter_receives_batches():
    storage = MemoryStorage()
    exported = []

    class FakeExporter:
        async def export(self, spans):
            exported.extend(spans)

        async def shutdown(self):
            pass

    recorder = Recorder(storage=storage, exporters=[FakeExporter()], batch_size=1, flush_interval=0.05).start()
    try:
        recorder.on_span_end(make_span(id="x"))
        ok = await _wait_until(lambda: len(exported) == 1)
        assert ok
    finally:
        recorder.stop()


async def test_on_span_start_is_a_noop():
    storage = MemoryStorage()
    recorder = Recorder(storage=storage).start()
    try:
        recorder.on_span_start(make_span())  # should not raise or record
        await asyncio.sleep(0.1)
        assert len(storage) == 0
    finally:
        recorder.stop()


def test_start_is_idempotent():
    recorder = Recorder(storage=MemoryStorage())
    recorder.start()
    recorder.start()  # must not spawn a second thread / raise
    recorder.stop()
