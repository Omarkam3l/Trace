"""FastAPI auto-instrumentation.

Implements traceforge.instrumentation.base.Instrumentor for FastAPI apps:
every incoming request becomes a SERVER-kind span on the Tracer passed to
install(), with HTTP method/path/status recorded as attributes and
exceptions captured automatically (the same as any other TraceForge span).

Usage::

    app = FastAPI()
    tracer = traceforge.configure(service_name="my-api")

    instrumentor = FastAPIInstrumentor(app)
    instrumentor.install(tracer)

    # ... app runs, requests are now traced ...

    instrumentor.uninstall()

Known limitation: Starlette (which FastAPI is built on) does not support
removing middleware after the ASGI middleware stack has been built, which
typically happens on first request or app startup. uninstall() therefore
cannot physically detach the middleware -- instead it flips a shared,
thread-safe flag that the middleware checks on every request, making it a
pure passthrough. This gives you working start/stop semantics without
lying about what's happening in the ASGI stack.
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from traceforge.instrumentation.base import Instrumentor
from traceforge.models.enums import SpanKind, SpanStatus

if TYPE_CHECKING:
    from fastapi import FastAPI

    from traceforge.core.tracer import Tracer


class _InstrumentorState:
    """Mutable, shared toggle between FastAPIInstrumentor and the running

    middleware instance. See module docstring for why this exists instead of
    literally removing the middleware.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._enabled = True

    @property
    def enabled(self) -> bool:
        with self._lock:
            return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        with self._lock:
            self._enabled = value


class _TracingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, tracer: Tracer, state: _InstrumentorState) -> None:
        super().__init__(app)
        self._tracer = tracer
        self._state = state

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not self._state.enabled:
            return await call_next(request)

        span_name = f"{request.method} {request.url.path}"
        async with self._tracer.start_span(
            span_name,
            kind=SpanKind.SERVER,
            attributes={
                "http.method": request.method,
                "http.path": request.url.path,
                "http.scheme": request.url.scheme,
            },
        ) as span:
            try:
                response = await call_next(request)
            except Exception as exc:
                span.record_exception(exc)
                span.set_status(SpanStatus.ERROR)
                raise
            span.set_attribute("http.status_code", response.status_code)
            if response.status_code >= 500:
                span.set_status(SpanStatus.ERROR)
            return response


class FastAPIInstrumentor(Instrumentor):
    """Auto-instruments a FastAPI app: every request becomes a TraceForge span."""

    def __init__(self, app: FastAPI) -> None:
        self._app = app
        self._state = _InstrumentorState()
        self._installed = False

    def install(self, tracer: Tracer) -> None:
        if self._installed:
            raise RuntimeError(
                "FastAPIInstrumentor.install() was already called for this app. "
                "Call uninstall() first if you need to reconfigure it."
            )
        self._app.add_middleware(_TracingMiddleware, tracer=tracer, state=self._state)
        self._installed = True

    def uninstall(self) -> None:
        # See module docstring: this disables tracing via the shared state
        # flag rather than removing the middleware from the ASGI stack,
        # which Starlette does not support after the stack is built.
        self._state.enabled = False
        self._installed = False
