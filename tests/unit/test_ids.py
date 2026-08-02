"""Unit tests for traceforge.core.ids."""

from __future__ import annotations

from traceforge.core.ids import (
    generate_correlation_id,
    generate_event_id,
    generate_session_id,
    generate_span_id,
    generate_trace_id,
)


def test_trace_id_is_32_hex_chars():
    trace_id = generate_trace_id()
    assert len(trace_id) == 32
    int(trace_id, 16)  # doesn't raise


def test_span_id_is_16_hex_chars():
    span_id = generate_span_id()
    assert len(span_id) == 16
    int(span_id, 16)


def test_ids_are_unique():
    ids = {generate_trace_id() for _ in range(1000)}
    assert len(ids) == 1000


def test_correlation_and_session_ids_are_distinct_functions():
    assert generate_correlation_id() != generate_session_id()


def test_event_id_generation():
    assert len(generate_event_id()) == 16
