"""Unit tests for traceforge.storage.jsonl.JSONLStorage."""

from __future__ import annotations

from datetime import UTC, datetime

from traceforge.models.enums import SpanKind, SpanStatus
from traceforge.models.span import SpanModel
from traceforge.storage.jsonl import JSONLStorage


def make_span(**overrides) -> SpanModel:
    defaults = dict(
        id="s1",
        trace_id="t1",
        name="x",
        kind=SpanKind.INTERNAL,
        status=SpanStatus.OK,
        start_time=datetime.now(UTC),
    )
    defaults.update(overrides)
    return SpanModel(**defaults)


async def test_creates_parent_directories(tmp_jsonl_path):
    storage = JSONLStorage(tmp_jsonl_path)
    await storage.write_spans([make_span()])
    assert tmp_jsonl_path.exists()


async def test_write_and_query_roundtrip(tmp_jsonl_path):
    storage = JSONLStorage(tmp_jsonl_path)
    span = make_span()
    await storage.write_spans([span])
    results = await storage.query_spans(trace_id="t1")
    assert len(results) == 1
    assert results[0].id == span.id
    assert results[0].name == span.name


async def test_appends_across_multiple_writes(tmp_jsonl_path):
    storage = JSONLStorage(tmp_jsonl_path)
    await storage.write_spans([make_span(id="a")])
    await storage.write_spans([make_span(id="b")])
    results = await storage.query_spans()
    assert {s.id for s in results} == {"a", "b"}
    # exactly two lines on disk
    assert len(tmp_jsonl_path.read_text().strip().splitlines()) == 2


async def test_empty_write_is_noop(tmp_jsonl_path):
    storage = JSONLStorage(tmp_jsonl_path)
    await storage.write_spans([])
    assert await storage.query_spans() == []


async def test_query_on_nonexistent_file_returns_empty(tmp_path):
    storage = JSONLStorage(tmp_path / "nope.jsonl")
    assert await storage.query_spans() == []
