"""Convenience, process-wide default-tracer functions.

TraceForge's core (`Tracer`, `Span`, `ContextManager`, ...) holds **no**
global mutable state — every ``Tracer`` is an explicit, independent object.
This module is the *one intentional, opt-in exception*: a small, guarded
"default tracer" registry for applications that don't want to thread a
``Tracer`` instance through every call site. Using it is entirely optional;
nothing in ``traceforge.core`` depends on it.
"""

from __future__ import annotations

import threading
from contextvars import Token
from typing import Any

from traceforge.api.exceptions import TracerNotConfiguredError
from traceforge.core.context import ContextManager, ExecutionContext
from traceforge.core.ids import generate_correlation_id, generate_session_id
from traceforge.core.tracer import Tracer

_default_tracer: Tracer | None = None
_lock = threading.Lock()


def configure(
    tracer: Tracer | str | None = None,
    *,
    service_name: str | None = None,
    **kwargs: Any,
) -> Tracer:
    """Register process-wide default Tracer.

    Can be called with an existing ``Tracer`` instance, or with keyword arguments /
    service name string to construct a new ``Tracer``.

    Examples:
        traceforge.configure(service_name="my-service")
        traceforge.configure("my-service")
        traceforge.configure(tracer)
        traceforge.configure(tracer=tracer)
    """
    global _default_tracer
    if isinstance(tracer, Tracer):
        inst = tracer
    elif isinstance(tracer, str):
        inst = Tracer(service_name=tracer, **kwargs)
    elif service_name is not None:
        inst = Tracer(service_name=service_name, **kwargs)
    elif tracer is None:
        inst = Tracer(service_name="default", **kwargs)
    else:
        raise TypeError(f"Invalid argument type for configure: {type(tracer).__name__}")

    with _lock:
        _default_tracer = inst
    return inst



def get_tracer() -> Tracer:
    """Return the configured default tracer.

    Raises :class:`TracerNotConfiguredError` if :func:`configure` was
    never called.
    """
    with _lock:
        if _default_tracer is None:
            raise TracerNotConfiguredError(
                "no default Tracer configured; call traceforge.configure(tracer) first, "
                "or use a Tracer instance directly."
            )
        return _default_tracer


def is_configured() -> bool:
    with _lock:
        return _default_tracer is not None


def reset_default_tracer() -> None:
    """Clear the default tracer. Primarily useful in tests."""
    global _default_tracer
    with _lock:
        _default_tracer = None


# -- context convenience -------------------------------------------------
def current_trace_id() -> str | None:
    return ContextManager.get_current().trace_id


def current_span_id() -> str | None:
    return ContextManager.get_current().span_id


def current_correlation_id() -> str | None:
    return ContextManager.get_current().correlation_id


def current_session_id() -> str | None:
    return ContextManager.get_current().session_id


def set_correlation_id(correlation_id: str | None = None) -> Token[ExecutionContext]:
    """Bind a correlation ID onto the current execution context.

    Returns a token that can be passed to ``ContextManager.reset`` to undo
    the change (e.g. at the end of a request).
    """
    ctx = ContextManager.get_current()
    new_ctx = ExecutionContext(
        trace_id=ctx.trace_id,
        span_id=ctx.span_id,
        parent_span_id=ctx.parent_span_id,
        correlation_id=correlation_id or generate_correlation_id(),
        session_id=ctx.session_id,
    )
    return ContextManager.set_current(new_ctx)


def new_session(session_id: str | None = None) -> Token[ExecutionContext]:
    """Bind a (new, by default) session ID onto the current execution context."""
    ctx = ContextManager.get_current()
    new_ctx = ExecutionContext(
        trace_id=ctx.trace_id,
        span_id=ctx.span_id,
        parent_span_id=ctx.parent_span_id,
        correlation_id=ctx.correlation_id,
        session_id=session_id or generate_session_id(),
    )
    return ContextManager.set_current(new_ctx)
