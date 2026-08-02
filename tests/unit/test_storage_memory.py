"""Unit tests for traceforge.storage.memory.MemoryStorage."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from traceforge.models.enums import SpanKind, SpanStatus
from traceforge.models.span import SpanModel
from traceforge.storage.memory import MemoryStorage


def make_span(**overrides) -> SpanModel:
    defaults = dict(
        id="s1",
        trace_id="t1",
        name="x",
        kind=SpanKind.INTERNAL,
        status=SpanStatus.OK,
        start_time=datetime.now(timezone.utc),
        correlation_id="c1",
    )
    defaults.update(overrides)
    return SpanModel(**defaults)


async def test_write_and_query_roundtrip():
    storage = MemoryStorage()
    span = make_span()
    await storage.write_spans([span])
    results = await storage.query_spans(trace_id="t1")
    assert results == [span]


async def test_query_filters_by_trace_id():
    storage = MemoryStorage()
    await storage.write_spans([make_span(id="a", trace_id="t1"), make_span(id="b", trace_id="t2")])
    results = await storage.query_spans(trace_id="t1")
    assert [s.id for s in results] == ["a"]


async def test_query_filters_by_correlation_id():
    storage = MemoryStorage()
    await storage.write_spans(
        [make_span(id="a", correlation_id="c1"), make_span(id="b", correlation_id="c2")]
    )
    results = await storage.query_spans(correlation_id="c2")
    assert [s.id for s in results] == ["b"]


async def test_respects_limit():
    storage = MemoryStorage()
    await storage.write_spans([make_span(id=str(i)) for i in range(10)])
    results = await storage.query_spans(limit=3)
    assert len(results) == 3


async def test_bounded_by_max_spans():
    storage = MemoryStorage(max_spans=5)
    await storage.write_spans([make_span(id=str(i)) for i in range(10)])
    assert len(storage) == 5


async def test_context_manager_closes():
    async with MemoryStorage() as storage:
        await storage.write_spans([make_span()])
    # close() is a no-op for memory storage; just verify no exception
