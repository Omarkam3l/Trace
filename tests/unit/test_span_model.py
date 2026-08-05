"""Unit tests for traceforge.models.span.SpanModel."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.models.enums import SpanKind, SpanStatus
from traceforge.models.span import SpanModel


def make_span(**overrides) -> SpanModel:
    defaults = dict(id="s1", trace_id="t1", name="x", start_time=datetime.now(timezone.utc))
    defaults.update(overrides)
    return SpanModel(**defaults)


def test_defaults():
    span = make_span()
    assert span.kind is SpanKind.INTERNAL
    assert span.status is SpanStatus.UNSET
    assert span.attributes == {}
    assert span.events == []
    assert span.is_root is True
    assert span.is_finished is False


def test_is_root_false_when_parent_present():
    span = make_span(parent_span_id="parent-1")
    assert span.is_root is False


def test_is_finished_true_once_end_time_set():
    span = make_span(end_time=datetime.now(timezone.utc))
    assert span.is_finished is True


def test_span_model_is_frozen():
    import pytest
    from pydantic import ValidationError

    span = make_span()
    with pytest.raises(ValidationError):
        span.name = "changed"  # type: ignore[misc]


def test_json_roundtrip():
    span = make_span()
    restored = SpanModel.model_validate_json(span.model_dump_json())
    assert restored == span
