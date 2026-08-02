"""Lightweight performance sanity checks (not a substitute for the
dedicated benchmarks/ suite — these just guard against gross regressions
in the hot path).
"""

from __future__ import annotations

import time

from traceforge.core.tracer import Tracer


def test_creating_many_spans_stays_fast():
    tracer = Tracer("perf-service")
    iterations = 5_000

    start = time.perf_counter()
    for _ in range(iterations):
        with tracer.start_span("perf-span") as span:
            span.set_attribute("k", "v")
    elapsed = time.perf_counter() - start

    per_span_us = (elapsed / iterations) * 1_000_000
    # Generous ceiling to stay robust across CI/dev hardware while still
    # catching an accidental O(n^2) or similar regression.
    assert per_span_us < 500, f"span overhead too high: {per_span_us:.1f}us/span"


def test_nested_spans_stay_fast():
    tracer = Tracer("perf-service")
    iterations = 1_000

    start = time.perf_counter()
    for _ in range(iterations):
        with tracer.start_span("outer"):
            with tracer.start_span("inner"):
                pass
    elapsed = time.perf_counter() - start

    per_iteration_us = (elapsed / iterations) * 1_000_000
    assert per_iteration_us < 1000, f"nested span overhead too high: {per_iteration_us:.1f}us"
