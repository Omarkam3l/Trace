"""Unit tests for QueryFilter model."""

from __future__ import annotations

from datetime import UTC, datetime

from traceforge.query.filters import QueryFilter


def test_query_filter_creation_and_immutability():
    now = datetime.now(UTC)
    flt = QueryFilter(
        session_id="s1",
        status="completed",
        timestamp_from=now,
    )
    assert flt.session_id == "s1"
    assert flt.status == "completed"
    assert flt.timestamp_from == now
