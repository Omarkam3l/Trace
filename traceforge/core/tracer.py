"""The Tracer: TraceForge's main entry point for capturing execution flow.

Design notes
------------
- **Async-first, sync-compatible**: ``start_span`` returns a context manager
  usable as both ``with`` and ``async with``. The bookkeeping itself
  (allocating IDs, computing durations) is synchronous and fast — there is
  nothing to ``await`` — so both call styles are first-class, not one
  emulating the other.
- **No global mutable state**: a ``Tracer`` instance owns its own
  :class:`~traceforge.core.lifecycle.LifecycleManager` and trace registry.
  Multiple independent tracers can coexist in the same process.
- **Thread-safe**: the trace registry is guarded by a lock; per-span
  mutation safety is handled by :class:`~traceforge.core.span.Span` itself.
- **Context propagation**: parent-child relationships and correlation/session
  IDs flow automatically via :class:`~traceforge.core.context.ContextManager`
  (``contextvars``), which is safe across both threads and asyncio tasks.
"""

from __future__ import annotations

import threading
from types import TracebackType
from typing import Any, Literal

from traceforge.core.clock import Clock, SystemClock
from traceforge.core.context import ContextManager, ExecutionContext
from traceforge.core.ids import generate_correlation_id, generate_span_id, generate_trace_id
from traceforge.core.lifecycle import LifecycleManager, SpanLifecycleHook
from traceforge.core.span import Span
from traceforge.core.trace import Trace
from traceforge.models.enums import SpanKind, SpanStatus
from traceforge.models.metadata import Attributes, sanitize_attributes
from traceforge.models.span import SpanModel


class Tracer:
    """Captures nested, parent-linked spans of execution.

    Not a logger, not an APM, and not business-logic aware: a ``Tracer``
    only knows about spans, events, and their timing/structure.
    """

    def __init__(self, service_name: str, *, clock: Clock | None = None) -> None:
        self._service_name = service_name
        self._clock: Clock = clock or SystemClock()
        self._lifecycle = LifecycleManager()
        self._traces: dict[str, Trace] = {}
        self._lock = threading.RLock()

    @property
    def service_name(self) -> str:
        return self._service_name

    # -- hook management ----------------------------------------------
    def add_hook(self, hook: SpanLifecycleHook) -> None:
        """Register something (typically a Recorder) to observe span lifecycle."""
        self._lifecycle.register(hook)

    def remove_hook(self, hook: SpanLifecycleHook) -> None:
        self._lifecycle.unregister(hook)

    # -- public API -----------------------------------------------------
    def start_trace(
        self,
        name: str,
        *,
        correlation_id: str | None = None,
        session_id: str | None = None,
    ) -> Trace:
        """Start a new trace and return its Trace handle.

        Example::

            trace = tracer.start_trace("Login")
            span = trace.start_span("Database")
            span.add_event("SELECT user")
            span.finish()
            trace.finish()
        """
        trace_id = generate_trace_id()
        corr_id = correlation_id or ContextManager.get_current().correlation_id or generate_correlation_id()
        sess_id = session_id or ContextManager.get_current().session_id

        trace = Trace(
            trace_id=trace_id,
            correlation_id=corr_id,
            session_id=sess_id,
            name=name,
            tracer=self,
        )
        with self._lock:
            self._traces[trace_id] = trace

        # Register active tracer on context manager
        ContextManager._active_tracer = self

        # Start root span for trace
        root_span, _token = self._begin_span(
            name=name,
            kind=SpanKind.INTERNAL,
            attributes=None,
            trace_id=trace_id,
        )
        with trace._lock:
            trace._active_spans.append(root_span)

        return trace

    def start_span(
        self,
        name: str,
        *,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Attributes | None = None,
    ) -> SpanContext:
        """Start a new span as a context manager.

        Usable both ways::

            with tracer.start_span("load-config") as span:
                ...

            async with tracer.start_span("fetch-user") as span:
                ...
        """
        return SpanContext(self, name, kind, attributes)

    def current_span_id(self) -> str | None:
        return ContextManager.get_current().span_id

    def current_trace_id(self) -> str | None:
        return ContextManager.get_current().trace_id

    # -- internal: used by SpanContext & Trace ---------------------------
    def _begin_span(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Attributes | None = None,
        trace_id: str | None = None,
        parent_span_id: str | None = None,
    ) -> tuple[Span, Any]:
        parent_ctx = ContextManager.get_current()
        effective_trace_id = trace_id or parent_ctx.trace_id or generate_trace_id()
        effective_parent_span_id = parent_span_id if parent_span_id is not None else parent_ctx.span_id
        span_id = generate_span_id()

        correlation_id = parent_ctx.correlation_id
        if correlation_id is None:
            correlation_id = generate_correlation_id()

        start_monotonic = self._clock.monotonic()
        model = SpanModel(
            id=span_id,
            trace_id=effective_trace_id,
            parent_span_id=effective_parent_span_id,
            name=name,
            kind=kind,
            status=SpanStatus.RUNNING,
            start_time=self._clock.now(),
            attributes=sanitize_attributes(attributes),
            correlation_id=correlation_id,
            session_id=parent_ctx.session_id,
        )
        trace = self._get_or_create_trace(effective_trace_id, correlation_id, parent_ctx.session_id, name=name)
        span = Span(model, self._clock, start_monotonic, tracer=self, trace=trace)
        trace.register_span_start(model)

        self._lifecycle.notify_start(model)

        new_ctx = ExecutionContext(
            trace_id=effective_trace_id,
            span_id=span_id,
            parent_span_id=effective_parent_span_id,
            correlation_id=correlation_id,
            session_id=parent_ctx.session_id,
        )
        token = ContextManager.set_current(new_ctx)
        span._token = token
        return span, token

    def _end_span(self, span: Span, token: Any, exc: BaseException | None) -> None:
        try:
            if exc is not None:
                span.record_exception(exc)
                span.set_status(SpanStatus.ERROR)
            elif span.status is SpanStatus.UNSET or span.status is SpanStatus.RUNNING:
                span.set_status(SpanStatus.OK)
            finished = span.finish()
        finally:
            if token is not None:
                ContextManager.reset(token)

        trace = self._traces.get(finished.trace_id)
        if trace is not None:
            was_root = trace.register_span_end(finished)
            if was_root and trace.is_complete():
                with self._lock:
                    self._traces.pop(finished.trace_id, None)

        self._lifecycle.notify_end(finished)

    def _get_or_create_trace(
        self,
        trace_id: str,
        correlation_id: str | None,
        session_id: str | None,
        name: str = "trace",
    ) -> Trace:
        with self._lock:
            trace = self._traces.get(trace_id)
            if trace is None:
                trace = Trace(
                    trace_id=trace_id,
                    correlation_id=correlation_id,
                    session_id=session_id,
                    name=name,
                    tracer=self,
                )
                self._traces[trace_id] = trace
            return trace

    def active_trace_count(self) -> int:
        """Number of traces with at least one still-open span. Mostly for tests."""
        with self._lock:
            return len(self._traces)


class SpanContext:
    """Context manager returned by :meth:`Tracer.start_span`.

    Supports both ``with`` and ``async with`` because the underlying work
    (ID allocation, timing) is synchronous; the async variant exists purely
    for ergonomics inside ``async def`` functions.
    """

    __slots__ = ("_attributes", "_kind", "_name", "_span", "_token", "_tracer")

    def __init__(
        self,
        tracer: Tracer,
        name: str,
        kind: SpanKind,
        attributes: Attributes | None,
    ) -> None:
        self._tracer = tracer
        self._name = name
        self._kind = kind
        self._attributes = attributes
        self._span: Span | None = None
        self._token: Any = None

    def __enter__(self) -> Span:
        self._span, self._token = self._tracer._begin_span(self._name, self._kind, self._attributes)
        return self._span

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> Literal[False]:
        assert self._span is not None
        self._tracer._end_span(self._span, self._token, exc)
        return False

    async def __aenter__(self) -> Span:
        return self.__enter__()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> Literal[False]:
        return self.__exit__(exc_type, exc, tb)
