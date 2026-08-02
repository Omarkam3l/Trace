"""Unit tests for traceforge.models.trace.TraceModel."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from traceforge.models.span import SpanModel
from traceforge.models.trace import TraceModel


def _span(id, parent=None, start_offset=0, end_offset=None, correlation_id="c1"):
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return SpanModel(
        id=id,
        trace_id="t1",
        parent_span_id=parent,
        name=id,
        start_time=base + timedelta(seconds=start_offset),
        end_time=base + timedelta(seconds=end_offset) if end_offset is not None else None,
        correlation_id=correlation_id,
    )


def test_from_spans_identifies_root_and_bounds():
    spans = [_span("root", start_offset=0, end_offset=5), _span("child", parent="root", start_offset=1, end_offset=3)]
    trace = TraceModel.from_spans("t1", spans)
    assert trace.root_span_id == "root"
    assert trace.correlation_id == "c1"
    assert trace.start_time == spans[0].start_time
    assert trace.end_time == spans[0].end_time  # latest end time


def test_from_spans_raises_on_empty_list():
    with pytest.raises(ValueError):
        TraceModel.from_spans("t1", [])


def test_end_time_none_if_any_span_unfinished():
    spans = [_span("root", end_offset=5), _span("child", parent="root", end_offset=None)]
    trace = TraceModel.from_spans("t1", spans)
    assert trace.end_time is None
