"""The Trace domain object: tracks aggregate state for one trace ID.

Kept intentionally light — TraceForge does not hold whole traces in memory
forever. This object's job is only to know the trace's root span and
overall span count so the Tracer can answer cheap questions like
"has this trace's root span finished?" without querying storage.
"""

from __future__ import annotations

import threading

from traceforge.models.span import SpanModel


from datetime import datetime
from typing import Any

from traceforge.models.enums import EventLevel, SpanKind, SpanStatus
from traceforge.models.metadata import Attributes
from traceforge.models.span import SpanModel
from traceforge.models.trace import TraceModel


class Trace:
    """Tracks bookkeeping for a single trace as spans are opened/closed."""

    __slots__ = (
        "_id",
        "_name",
        "_correlation_id",
        "_session_id",
        "_root_span_id",
        "_lock",
        "_open_span_count",
        "_tracer",
        "_started_at",
        "_finished_at",
        "_duration_ms",
        "_status",
        "_spans",
        "_active_spans",
        "_start_monotonic",
    )

    def __init__(
        self,
        trace_id: str,
        correlation_id: str | None = None,
        session_id: str | None = None,
        name: str = "trace",
        tracer: Any | None = None,
    ) -> None:
        self._id = trace_id
        self._name = name
        self._correlation_id = correlation_id
        self._session_id = session_id
        self._root_span_id: str | None = None
        self._open_span_count = 0
        self._lock = threading.RLock()
        self._tracer = tracer
        self._started_at = tracer._clock.now() if tracer else datetime.now()
        self._start_monotonic = tracer._clock.monotonic() if tracer else 0.0
        self._finished_at: datetime | None = None
        self._duration_ms: float | None = None
        self._status: SpanStatus = SpanStatus.RUNNING
        self._spans: list[SpanModel] = []
        self._active_spans: list[Any] = []

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def correlation_id(self) -> str | None:
        return self._correlation_id

    @property
    def session_id(self) -> str | None:
        return self._session_id

    @property
    def root_span_id(self) -> str | None:
        with self._lock:
            return self._root_span_id

    @property
    def started_at(self) -> datetime:
        return self._started_at

    @property
    def start_time(self) -> datetime:
        return self._started_at

    @property
    def finished_at(self) -> datetime | None:
        with self._lock:
            return self._finished_at

    @property
    def end_time(self) -> datetime | None:
        with self._lock:
            return self._finished_at

    @property
    def duration_ms(self) -> float | None:
        with self._lock:
            return self._duration_ms

    @property
    def status(self) -> SpanStatus:
        with self._lock:
            return self._status

    @property
    def root_span(self) -> SpanModel | None:
        with self._lock:
            if not self._spans:
                return None
            return next((s for s in self._spans if s.is_root), self._spans[0])

    @property
    def spans(self) -> list[SpanModel]:
        with self._lock:
            return list(self._spans)

    def start_span(
        self,
        name: str,
        *,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Attributes | None = None,
    ) -> Any:
        """Start a new span within this trace."""
        if self._tracer is None:
            raise RuntimeError("Tracer not bound to Trace instance")
        span, _ = self._tracer._begin_span(
            name=name,
            kind=kind,
            attributes=attributes,
            trace_id=self._id,
        )
        with self._lock:
            self._active_spans.append(span)
        return span

    def add_event(
        self,
        name: str,
        attributes: Attributes | None = None,
        level: EventLevel = EventLevel.INFO,
    ) -> Trace:
        """Add an event to the currently active span or root span of this trace."""
        with self._lock:
            target_span = self._active_spans[-1] if self._active_spans else None
        if target_span is not None:
            target_span.add_event(name, attributes=attributes, level=level)
        return self

    def register_span_start(self, span: SpanModel) -> None:
        with self._lock:
            if span.is_root and self._root_span_id is None:
                self._root_span_id = span.id
            self._open_span_count += 1
            idx = next((i for i, s in enumerate(self._spans) if s.id == span.id), None)
            if idx is None:
                self._spans.append(span)
            else:
                self._spans[idx] = span

    def register_span_end(self, span: SpanModel) -> bool:
        """Returns True if this was the trace's root span finishing."""
        with self._lock:
            self._open_span_count = max(0, self._open_span_count - 1)
            idx = next((i for i, s in enumerate(self._spans) if s.id == span.id), None)
            if idx is not None:
                self._spans[idx] = span
            else:
                self._spans.append(span)
            was_root = span.id == self._root_span_id
            if was_root and self._open_span_count == 0 and self._tracer is not None:
                with self._tracer._lock:
                    self._tracer._traces.pop(self._id, None)
            return was_root

    def is_complete(self) -> bool:
        with self._lock:
            return self._open_span_count == 0 and self._root_span_id is not None

    def finish(self, status: SpanStatus = SpanStatus.SUCCESS) -> TraceModel:
        """Finish the trace and all open spans, computing duration and status."""
        with self._lock:
            # Finish any still-open active spans in reverse creation order
            for span in reversed(list(self._active_spans)):
                if not span.is_finished:
                    span.finish()

            if self._tracer is not None:
                clock = self._tracer._clock
                self._finished_at = clock.now()
                self._duration_ms = max(0.0, (clock.monotonic() - self._start_monotonic) * 1000.0)
            else:
                self._finished_at = datetime.now()
                self._duration_ms = 0.0

            if status is SpanStatus.OK:
                status = SpanStatus.SUCCESS

            self._status = status
            return TraceModel.from_spans(
                self._id,
                self._spans,
                name=self._name,
                status=self._status,
            )
