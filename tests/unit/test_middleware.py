"""Unit tests for traceforge.middleware."""

from __future__ import annotations

from traceforge.middleware.correlation import extract_correlation_id, inject_correlation_id
from traceforge.middleware.timing import timed_call, timed_call_async


def test_extract_correlation_id_case_insensitive():
    headers = {"x-correlation-id": "abc123"}
    assert extract_correlation_id(headers) == "abc123"


def test_extract_correlation_id_missing_returns_none():
    assert extract_correlation_id({}) is None


def test_inject_correlation_id_generates_when_absent():
    headers: dict[str, str] = {}
    cid = inject_correlation_id(headers)
    assert headers["X-Correlation-ID"] == cid
    assert len(cid) == 32


def test_inject_correlation_id_uses_provided_value():
    headers: dict[str, str] = {}
    cid = inject_correlation_id(headers, "fixed-id")
    assert cid == "fixed-id"
    assert headers["X-Correlation-ID"] == "fixed-id"


def test_timed_call_reports_elapsed():
    result, elapsed_ms = timed_call(lambda: 42)
    assert result == 42
    assert elapsed_ms >= 0


async def test_timed_call_async_reports_elapsed():
    async def work():
        return "done"

    result, elapsed_ms = await timed_call_async(work)
    assert result == "done"
    assert elapsed_ms >= 0
