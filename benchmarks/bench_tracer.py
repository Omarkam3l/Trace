"""Simple throughput/overhead benchmarks for the Tracer hot path.

Not a substitute for a proper benchmarking harness (pytest-benchmark,
etc.) — just a quick, dependency-free way to sanity-check overhead
locally: ``python benchmarks/bench_tracer.py``.
"""

from __future__ import annotations

import statistics
import time

from traceforge.core.tracer import Tracer


def bench_flat_spans(n: int = 20_000) -> None:
    tracer = Tracer("bench-service")
    start = time.perf_counter()
    for _ in range(n):
        with tracer.start_span("flat-span") as span:
            span.set_attribute("k", "v")
    elapsed = time.perf_counter() - start
    print(f"flat spans:   {n:>7} spans in {elapsed:.3f}s  ({(elapsed / n) * 1e6:.2f}us/span)")


def bench_nested_spans(n: int = 5_000, depth: int = 4) -> None:
    tracer = Tracer("bench-service")

    def recurse(remaining: int) -> None:
        if remaining == 0:
            return
        with tracer.start_span(f"level-{remaining}"):
            recurse(remaining - 1)

    start = time.perf_counter()
    for _ in range(n):
        recurse(depth)
    elapsed = time.perf_counter() - start
    total_spans = n * depth
    print(
        f"nested spans: {total_spans:>7} spans in {elapsed:.3f}s "
        f"({(elapsed / total_spans) * 1e6:.2f}us/span, depth={depth})"
    )


def bench_with_hook(n: int = 20_000) -> None:
    tracer = Tracer("bench-service")
    durations = []

    class TimingHook:
        def on_span_start(self, span):
            pass

        def on_span_end(self, span):
            durations.append(span.duration_ms)

    tracer.add_hook(TimingHook())
    start = time.perf_counter()
    for _ in range(n):
        with tracer.start_span("hooked-span"):
            pass
    elapsed = time.perf_counter() - start
    print(
        f"with hook:    {n:>7} spans in {elapsed:.3f}s  ({(elapsed / n) * 1e6:.2f}us/span), "
        f"mean recorded duration={statistics.mean(durations):.4f}ms"
    )


if __name__ == "__main__":
    bench_flat_spans()
    bench_nested_spans()
    bench_with_hook()
