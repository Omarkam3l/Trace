"""Function decorators for automatic tracing.

Detects sync vs. async functions at decoration time and wraps each
appropriately, so a single decorator works for both execution styles.
"""

from __future__ import annotations

import functools
import inspect
from collections.abc import Callable
from typing import Any, TypeVar

from traceforge.api.functions import get_tracer
from traceforge.core.tracer import Tracer
from traceforge.models.enums import SpanKind
from traceforge.models.metadata import Attributes

F = TypeVar("F", bound=Callable[..., Any])


def traced(
    name: str | None = None,
    *,
    tracer: Tracer | None = None,
    kind: SpanKind = SpanKind.INTERNAL,
    attributes: Attributes | None = None,
    capture_return: bool = True,
) -> Callable[[F], F]:
    """Wrap a function (sync or async) so every call is captured as a span.

    Args:
        name: Span name. Defaults to the function's qualified name.
        tracer: Explicit tracer to use. Falls back to the configured
            default tracer (``traceforge.configure(...)``) if omitted.
        kind: The span's role (internal/client/server/...).
        attributes: Static attributes attached to every span this
            decorator creates.
        capture_return: If True (default), automatically records the return
            value as a ``result`` attribute on the span.
    """

    def decorator(func: F) -> F:
        span_name = name or func.__qualname__

        def _resolve_tracer() -> Tracer:
            return tracer if tracer is not None else get_tracer()

        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                span_ctx = _resolve_tracer().start_span(span_name, kind=kind, attributes=attributes)
                async with span_ctx as span:
                    res = await func(*args, **kwargs)
                    if capture_return:
                        span.set_attribute("result", res)
                    return res

            return async_wrapper  # type: ignore[return-value]

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            with _resolve_tracer().start_span(span_name, kind=kind, attributes=attributes) as span:
                res = func(*args, **kwargs)
                if capture_return:
                    span.set_attribute("result", res)
                return res

        return sync_wrapper  # type: ignore[return-value]

    return decorator
