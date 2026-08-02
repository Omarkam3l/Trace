"""Unit tests for the built-in exporters."""

from __future__ import annotations

import io
from datetime import datetime, timezone

from traceforge.exporters.console import ConsoleExporter
from traceforge.exporters.json import JSONExporter
from traceforge.models.enums import SpanKind, SpanStatus
from traceforge.models.span import SpanModel


def make_span(**overrides) -> SpanModel:
    defaults = dict(
        id="s1",
        trace_id="t1",
        name="x",
        kind=SpanKind.INTERNAL,
        status=SpanStatus.OK,
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        duration_ms=5.0,
    )
    defaults.update(overrides)
    return SpanModel(**defaults)


async def test_console_exporter_writes_one_line_per_span():
    stream = io.StringIO()
    exporter = ConsoleExporter(stream=stream, colorize=False)
    await exporter.export([make_span(id="a"), make_span(id="b")])
    lines = stream.getvalue().strip().splitlines()
    assert len(lines) == 2
    assert "x" in lines[0]


async def test_console_exporter_indents_child_spans():
    stream = io.StringIO()
    exporter = ConsoleExporter(stream=stream, colorize=False)
    await exporter.export([make_span(parent_span_id="parent-1")])
    line = stream.getvalue()
    assert line.startswith("  ")


async def test_json_exporter_requires_exactly_one_target():
    import pytest

    with pytest.raises(ValueError):
        JSONExporter()
    with pytest.raises(ValueError):
        JSONExporter(path="a.json", sink=lambda s: None)


async def test_json_exporter_sink_receives_payload():
    received = []
    exporter = JSONExporter(sink=received.append)
    await exporter.export([make_span()])
    assert len(received) == 1
    assert '"id": "s1"' in received[0] or '"id":"s1"' in received[0].replace(" ", "")


async def test_json_exporter_file_target(tmp_path):
    path = tmp_path / "out.json"
    exporter = JSONExporter(path=path)
    await exporter.export([make_span()])
    assert path.exists()
    assert "s1" in path.read_text()
