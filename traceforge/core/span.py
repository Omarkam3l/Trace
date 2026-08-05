"""The live, mutable Span domain object.

``SpanModel`` (in ``traceforge.models.span``) is an immutable snapshot;
``Span`` is the mutable object callers interact with while the span is
still open. Every mutation is guarded by a lock so concurrent callers
(e.g. a background thread attaching an event to a span another task
started) can't corrupt state.
"""

from __future__ import annotations

import threading
from datetime import datetime
from typing import Any, Self

from traceforge.core.clock import Clock
from traceforge.core.ids import generate_event_id
from traceforge.models.enums import EventLevel, SpanKind, SpanStatus
from traceforge.models.event import EventModel
from traceforge.models.metadata import Attributes, ExceptionInfo, sanitize_attributes
from traceforge.models.span import SpanModel


class Span:
    """A single, currently-open (or just-closed) unit of traced execution."""

    __slots__ = ("_clock", "_finished", "_lock", "_model", "_start_monotonic", "_token", "_trace", "_tracer")

    def __init__(
        self,
        model: SpanModel,
        clock: Clock,
        start_monotonic: float,
        tracer: Any | None = None,
        trace: Any | None = None,
    ) -> None:
        self._model = model
        self._clock = clock
        self._start_monotonic = start_monotonic
        self._lock = threading.RLock()
        self._finished = False
        self._tracer = tracer
        self._trace = trace
        self._token: Any = None

    # -- identity -----------------------------------------------------
    @property
    def id(self) -> str:
        return self._model.id

    @property
    def trace_id(self) -> str:
        return self._model.trace_id

    @property
    def parent_span_id(self) -> str | None:
        return self._model.parent_span_id

    @property
    def parent_id(self) -> str | None:
        return self._model.parent_span_id

    @property
    def name(self) -> str:
        return self._model.name

    @property
    def status(self) -> SpanStatus:
        with self._lock:
            return self._model.status

    @property
    def is_finished(self) -> bool:
        with self._lock:
            return self._finished

    @property
    def started_at(self) -> datetime:
        return self._model.start_time

    @property
    def finished_at(self) -> datetime | None:
        with self._lock:
            return self._model.end_time

    @property
    def duration_ms(self) -> float | None:
        with self._lock:
            return self._model.duration_ms

    @property
    def events(self) -> list[EventModel]:
        with self._lock:
            return list(self._model.events)

    @property
    def children(self) -> list[SpanModel]:
        with self._lock:
            return list(self._model.children)

    @property
    def attributes(self) -> Attributes:
        with self._lock:
            return dict(self._model.attributes)


    # -- nested span creation ------------------------------------------
    def start_span(
        self,
        name: str,
        *,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Attributes | None = None,
    ) -> Span:
        tracer = self._tracer
        if tracer is None:
            from traceforge.core.context import ContextManager

            tracer = getattr(ContextManager, "_active_tracer", None)
            if tracer is None:
                raise RuntimeError("No tracer available to start child span")
        return tracer._begin_span(
            name=name,
            kind=kind,
            attributes=attributes,
            trace_id=self.trace_id,
            parent_span_id=self.id,
        )[0]

    # -- mutation -------------------------------------------------------
    def set_attribute(self, key: str, value: object) -> Span:
        with self._lock:
            self._require_open()
            attrs = dict(self._model.attributes)
            attrs.update(sanitize_attributes({key: value}))
            self._model = self._model.model_copy(update={"attributes": attrs})
        return self

    def set_attributes(self, attributes: Attributes) -> Span:
        with self._lock:
            self._require_open()
            attrs = dict(self._model.attributes)
            attrs.update(sanitize_attributes(attributes))
            self._model = self._model.model_copy(update={"attributes": attrs})
        return self

    def add_event(
        self,
        name: str,
        attributes: Attributes | None = None,
        level: EventLevel = EventLevel.INFO,
    ) -> Span:
        event = EventModel(
            id=generate_event_id(),
            span_id=self.id,
            name=name,
            timestamp=self._clock.now(),
            level=level,
            attributes=sanitize_attributes(attributes),
        )
        with self._lock:
            self._require_open()
            events = [*self._model.events, event]
            self._model = self._model.model_copy(update={"events": events})
        return self

    def set_status(self, status: SpanStatus) -> Span:
        with self._lock:
            self._require_open()
            self._model = self._model.model_copy(update={"status": status})
        return self

    def record_exception(self, exc: BaseException) -> Span:
        info = ExceptionInfo.from_exception(exc)
        with self._lock:
            self._require_open()
            events = [
                *self._model.events,
                EventModel(
                    id=generate_event_id(),
                    span_id=self.id,
                    name="exception",
                    timestamp=self._clock.now(),
                    level=EventLevel.ERROR,
                    attributes={"exception.type": info.type, "exception.message": info.message},
                ),
            ]
            self._model = self._model.model_copy(update={"exception": info, "events": events})
        return self

    def set_kind(self, kind: SpanKind) -> Span:
        with self._lock:
            self._require_open()
            self._model = self._model.model_copy(update={"kind": kind})
        return self

    # -- context manager -------------------------------------------------
    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: Any,
    ) -> None:
        if exc is not None:
            self.record_exception(exc)
            self.set_status(SpanStatus.ERROR)
        elif self.status is SpanStatus.UNSET or self.status is SpanStatus.RUNNING:
            self.set_status(SpanStatus.OK)
        if self._tracer is not None:
            self._tracer._end_span(self, self._token, exc)
        else:
            self.finish()

    async def __aenter__(self) -> Self:
        return self.__enter__()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: Any,
    ) -> None:
        self.__exit__(exc_type, exc, tb)

    # -- lifecycle --------------------------------------------------------
    def snapshot(self) -> SpanModel:
        """An immutable copy of the span's state right now."""
        with self._lock:
            return self._model

    def finish(self) -> SpanModel:
        """Close the span, compute its duration, and return the final snapshot.

        Idempotent: calling ``finish()`` twice returns the same snapshot
        without re-computing duration.
        """
        with self._lock:
            if self._finished:
                return self._model
            end_time = self._clock.now()
            duration_ms = max(0.0, (self._clock.monotonic() - self._start_monotonic) * 1000.0)
            status = self._model.status
            if status is SpanStatus.UNSET or status is SpanStatus.RUNNING:
                status = SpanStatus.OK
            self._model = self._model.model_copy(
                update={"end_time": end_time, "duration_ms": duration_ms, "status": status}
            )
            self._finished = True
            finished_model = self._model

        if self._token is not None:
            from traceforge.core.context import ContextManager

            ContextManager.reset(self._token)
            self._token = None

        if self._trace is not None:
            self._trace.register_span_end(finished_model)

        return finished_model

    def _require_open(self) -> None:
        if self._finished:
            from traceforge.api.exceptions import SpanNotActiveError

            raise SpanNotActiveError(f"span {self._model.id!r} ({self._model.name!r}) has already finished")
