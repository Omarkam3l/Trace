"""Console exporter: pretty-prints finished spans to stdout.

Zero dependencies, zero configuration — the default choice for local
development and quick debugging.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from typing import TextIO

from traceforge.models.enums import SpanStatus
from traceforge.models.span import SpanModel

_STATUS_MARKS = {
    SpanStatus.OK: "OK",
    SpanStatus.ERROR: "ERROR",
    SpanStatus.UNSET: "UNSET",
}


class ConsoleExporter:
    """Writes a human-readable one-liner per span to a text stream in execution order."""

    def __init__(self, stream: TextIO | None = None, *, colorize: bool = True) -> None:
        self._stream = stream or sys.stdout
        self._colorize = colorize and self._stream.isatty()
        self._trace_buffers: dict[str, list[SpanModel]] = {}

    async def export(self, spans: Sequence[SpanModel]) -> None:
        if not spans:
            return

        for span in spans:
            self._trace_buffers.setdefault(span.trace_id, []).append(span)

        traces_to_flush = [
            t_id for t_id, buf in self._trace_buffers.items()
            if any(s.parent_span_id is None for s in buf)
        ]

        if not traces_to_flush:
            traces_to_flush = list(self._trace_buffers.keys())

        for t_id in traces_to_flush:
            self._flush_trace(t_id)

        self._stream.flush()

    def _flush_trace(self, trace_id: str) -> None:
        spans = self._trace_buffers.pop(trace_id, [])
        for span in sorted(spans, key=lambda s: s.start_time):
            self._stream.write(self._format(span) + "\n")

    def flush(self) -> None:
        for t_id in list(self._trace_buffers.keys()):
            self._flush_trace(t_id)
        self._stream.flush()

    def _format(self, span: SpanModel) -> str:
        indent = "  " if span.parent_span_id else ""
        duration = f"{span.duration_ms:.2f}ms" if span.duration_ms is not None else "?"
        status = _STATUS_MARKS.get(span.status, span.status.value)
        line = f"{indent}[{status}] {span.name} (trace={span.trace_id[:8]} span={span.id[:8]} duration={duration})"
        if self._colorize and span.status is SpanStatus.ERROR:
            return f"\x1b[31m{line}\x1b[0m"
        return line

    async def shutdown(self) -> None:
        self.flush()

