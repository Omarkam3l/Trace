"""Integration tests: Tracer -> Recorder -> Storage -> Exporter, end to end."""

from __future__ import annotations

import asyncio

import pytest

from traceforge.core.tracer import Tracer
from traceforge.exporters.console import ConsoleExporter
from traceforge.recorder.recorder import Recorder
from traceforge.storage.memory import MemoryStorage


async def _wait_until(predicate, timeout=3.0, interval=0.02):
    elapsed = 0.0
    while elapsed < timeout:
        if predicate():
            return True
        await asyncio.sleep(interval)
        elapsed += interval
    return False


async def test_nested_spans_flow_through_full_pipeline(frozen_clock):
    tracer = Tracer("integration-service", clock=frozen_clock)
    storage = MemoryStorage()
    recorder = Recorder(storage=storage, batch_size=10, flush_interval=0.05).start()
    tracer.add_hook(recorder)

    try:
        with tracer.start_span("http-request") as root:
            root.set_attribute("http.method", "GET")
            with tracer.start_span("db-query") as db:
                db.add_event("query-start")
                frozen_clock.advance(0.01)
            with tracer.start_span("cache-lookup"):
                frozen_clock.advance(0.005)

        ok = await _wait_until(lambda: len(storage) == 3)
        assert ok

        spans = await storage.query_spans(trace_id=root.trace_id, limit=10)
        assert len(spans) == 3

        by_name = {s.name: s for s in spans}
        assert by_name["db-query"].parent_span_id == by_name["http-request"].id
        assert by_name["cache-lookup"].parent_span_id == by_name["http-request"].id
        assert by_name["http-request"].parent_span_id is None
        assert by_name["http-request"].attributes["http.method"] == "GET"
        assert len(by_name["db-query"].events) == 1
    finally:
        recorder.stop()


async def test_exception_in_nested_span_propagates_status_only_to_that_span():
    tracer = Tracer("integration-service")
    storage = MemoryStorage()
    recorder = Recorder(storage=storage, batch_size=10, flush_interval=0.05).start()
    tracer.add_hook(recorder)

    try:
        with tracer.start_span("outer"):
            with pytest.raises(ValueError):
                with tracer.start_span("inner-fails"):
                    raise ValueError("nested boom")

        ok = await _wait_until(lambda: len(storage) == 2)
        assert ok
        spans = await storage.query_spans(limit=10)
        by_name = {s.name: s for s in spans}
        assert by_name["inner-fails"].status.value == "error"
        assert by_name["outer"].status.value == "ok"
    finally:
        recorder.stop()


async def test_mixed_sync_and_async_spans_in_one_trace():
    tracer = Tracer("integration-service")
    storage = MemoryStorage()
    recorder = Recorder(storage=storage, batch_size=10, flush_interval=0.05).start()
    tracer.add_hook(recorder)

    async def async_child():
        async with tracer.start_span("async-child"):
            await asyncio.sleep(0.01)

    try:
        with tracer.start_span("sync-root") as root:
            await async_child()

        ok = await _wait_until(lambda: len(storage) == 2)
        assert ok
        spans = await storage.query_spans(trace_id=root.trace_id, limit=10)
        assert {s.name for s in spans} == {"sync-root", "async-child"}
    finally:
        recorder.stop()


async def test_console_exporter_receives_finished_spans_via_recorder(capsys):
    tracer = Tracer("integration-service")
    storage = MemoryStorage()
    recorder = Recorder(
        storage=storage, exporters=[ConsoleExporter(colorize=False)], batch_size=1, flush_interval=0.05
    ).start()
    tracer.add_hook(recorder)

    try:
        with tracer.start_span("printed-span"):
            pass
        ok = await _wait_until(lambda: len(storage) == 1)
        assert ok
        await asyncio.sleep(0.05)  # give the exporter a moment after storage write
    finally:
        recorder.stop()

    captured = capsys.readouterr()
    assert "printed-span" in captured.out


async def test_high_concurrency_many_traces_stay_isolated():
    tracer = Tracer("integration-service")
    storage = MemoryStorage()
    recorder = Recorder(storage=storage, batch_size=20, flush_interval=0.05).start()
    tracer.add_hook(recorder)

    async def do_trace(n: int):
        async with tracer.start_span(f"root-{n}") as root:
            async with tracer.start_span(f"child-{n}") as child:
                assert child.trace_id == root.trace_id
                await asyncio.sleep(0.001)

    try:
        await asyncio.gather(*(do_trace(i) for i in range(30)))
        ok = await _wait_until(lambda: len(storage) == 60)
        assert ok
    finally:
        recorder.stop()
