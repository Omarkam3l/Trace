"""Unit tests for traceforge.storage.sqlite.SQLiteStorage."""

from __future__ import annotations

from datetime import UTC, datetime

from traceforge.models.enums import SpanKind, SpanStatus
from traceforge.models.event import EventModel
from traceforge.models.span import SpanModel
from traceforge.storage.sqlite import SQLiteStorage


def make_span(**overrides) -> SpanModel:
    defaults = dict(
        id="s1",
        trace_id="t1",
        name="x",
        kind=SpanKind.CLIENT,
        status=SpanStatus.OK,
        start_time=datetime.now(UTC),
        end_time=datetime.now(UTC),
        duration_ms=12.5,
        attributes={"a": 1},
        events=[EventModel(id="e1", name="ev", timestamp=datetime.now(UTC))],
    )
    defaults.update(overrides)
    return SpanModel(**defaults)


async def test_write_and_query_roundtrip(tmp_sqlite_path):
    storage = SQLiteStorage(tmp_sqlite_path)
    span = make_span()
    await storage.write_spans([span])
    results = await storage.query_spans(trace_id="t1")
    assert len(results) == 1
    row = results[0]
    assert row.id == span.id
    assert row.kind is SpanKind.CLIENT
    assert row.status is SpanStatus.OK
    assert row.attributes == {"a": 1}
    assert len(row.events) == 1
    assert row.duration_ms == 12.5
    await storage.close()


async def test_upsert_replaces_existing_row(tmp_sqlite_path):
    storage = SQLiteStorage(tmp_sqlite_path)
    await storage.write_spans([make_span(id="s1", name="first")])
    await storage.write_spans([make_span(id="s1", name="second")])
    results = await storage.query_spans(trace_id="t1")
    assert len(results) == 1
    assert results[0].name == "second"
    await storage.close()


async def test_persists_across_reconnect(tmp_sqlite_path):
    storage1 = SQLiteStorage(tmp_sqlite_path)
    await storage1.write_spans([make_span()])
    await storage1.close()

    storage2 = SQLiteStorage(tmp_sqlite_path)
    results = await storage2.query_spans()
    assert len(results) == 1
    await storage2.close()


async def test_query_respects_limit(tmp_sqlite_path):
    storage = SQLiteStorage(tmp_sqlite_path)
    await storage.write_spans([make_span(id=str(i), trace_id="t1") for i in range(10)])
    results = await storage.query_spans(trace_id="t1", limit=4)
    assert len(results) == 4
    await storage.close()
